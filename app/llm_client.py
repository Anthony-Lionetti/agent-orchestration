from groq import Groq
from groq.types.chat import ChatCompletionMessageParam, ChatCompletion
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from logging_service import get_system_logger
from logging_service.decorators import log_agent_actions, log_errors
from logging_service.utils import log_agent_interaction
from typing import List, Dict, TypedDict
from contextlib import AsyncExitStack
import json
import asyncio


class ToolDefinition(TypedDict):
    name: str
    description: str
    input_schema: dict


class MCPClient:
    def __init__(self, server_config_path:str="server_config.json", name:str="chatbot"):
        # Initialize session and client objects
        self.name = name
        self.sessions: List[ClientSession] = [] 
        self.exit_stack = AsyncExitStack() 
        self.groq = Groq()
        self.available_tools: List[ToolDefinition] = [] 
        self.tool_to_session: Dict[str, ClientSession] = {} 
        self.server_config_path = server_config_path
        self.logger = get_system_logger("mcp-client")

        self.logger.info(f"Initializing Chatbot with config: {server_config_path}")

        # Apply decorators dynamically using the instance name
        self._apply_dynamic_decorators()

    def _apply_dynamic_decorators(self) -> None:
        """Apply decorators that need access to instance attributes"""
        self.connect_to_server = log_agent_actions(self.name, 'connection')(self.connect_to_server)
        self.connect_to_server = log_errors()(self.connect_to_server)

        self.process_query = log_agent_actions(self.name, 'processing')(self.process_query)
        self.process_query = log_errors()(self.process_query)

    async def connect_to_server(self, server_name: str, server_config: dict) -> None:
        """
        Connect to a single MCP server.
        
        Parameters:
            server_name (str): Name of the MCP server to connect to 
            server_config (dict): Configuration details for the MCP server to connect to
        """
        self.logger.info(f"Attempting to connect to MCP server: {server_name}")

        try:
            server_params = StdioServerParameters(**server_config)
            stdio_transport = await self.exit_stack.enter_async_context(
                stdio_client(server_params)
            ) 
            read, write = stdio_transport
            session = await self.exit_stack.enter_async_context(
                ClientSession(read, write)
            ) 
            await session.initialize()
            self.sessions.append(session)
            
            # List available tools for this session
            response = await session.list_tools()
            tools = response.tools

            self.logger.debug(f"Connected to MCP server: {server_name} containing tools {[t.name for t in tools]}")
            
            for tool in tools: 
                self.tool_to_session[tool.name] = session
                self.available_tools.append({
                    "type": "function",
                    "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": {
                        "type": tool.inputSchema['type'],
                        "properties": tool.inputSchema['properties']
                    },
                    "required": tool.inputSchema['required']
                    }
                })
            
        except Exception as e:
            self.logger.error(f"Failed to connect to servers: {str(e)}")

    async def connect_to_servers(self): 
        """Connect to all configured MCP servers."""
        try:
            with open(self.server_config_path, "r") as file:
                data = json.load(file)
            
            servers = data.get("mcpServers", {})
            
            for server_name, server_config in servers.items():
                await self.connect_to_server(server_name, server_config)
        except Exception as e:
            self.logger.error(f"Error loading server config: {e}")
            raise
    
    async def process_query(self, query:str, model:str="meta-llama/llama-4-scout-17b-16e-instruct") -> str:
        log_agent_interaction(self.name, 'prompt_received', f"Prompt: {query}")

        # Take user query and generate assistant response
        messages:list[ChatCompletionMessageParam] = [{'role':'user', 'content':query}]
        response = self.groq.chat.completions.create(
                                        messages=messages,
                                        tools=self.available_tools,
                                        model=model
                                    )
        
        log_agent_interaction(self.name, 'assistant_response', f"Assistant responded with: {response.choices[0].message.content}")
        
        process_query = True
        while process_query:
            response_message = response.choices[0].message
            tool_names = [call.function.name for call in response_message.tool_calls] if response_message.tool_calls else []
            self.logger.debug(f"[MCP_ChatBot.process_query] - Response content: Role = {response_message.role} | Content = {response_message.content} {"| Tools " + str(tool_names) if tool_names else ""}\n\n")

            # Process the Assistant response
            assistant_and_tool_messages = self.__process_tool_calls(assistant_response=response, messages=messages, model=str)

            messages += assistant_and_tool_messages

            return messages

            # Process the Assistant response
            for choice in response.choices:
                self.logger.debug(f"[MCP_ChatBot.process_query] - Current choice: {choice}")

                # Get text content from assistant response
                response_content = choice.message.content
                messages.append({'role':'assistant', 'content':response_content})

                # Get tool use invokations from assistant response
                tool_calls = choice.message.tool_calls

                ####
                # Process each tool call
                self.logger.debug(f"Defined tool calls: {tool_calls}")
                if tool_calls is not None:
                    for tool_call in tool_calls:
                        tool_name = tool_call.function.name
                        tool_args:object = json.loads(tool_call.function.arguments)
                        log_agent_interaction(self.name, 'tool_call', f"Calling tool, {tool_name} with args {tool_args}")
                    
                        # Call a tool
                        session = self.tool_to_session[tool_name] 
                        # Await result of tool call
                        result = await session.call_tool(tool_name, arguments=tool_args)
                        log_agent_interaction(self.name, 'tool_call', f"Tool call results: {result.content}")


                        # Append tool call to chat history
                        messages.append(
                            {
                                "tool_call_id": tool_call.id, 
                                "role": "tool", # Indicates this message is from tool use
                                "name": tool_name,
                                "content": result.content
                            }
                        )

                    # generate next response 
                    response = self.groq.chat.completions.create(
                                        messages=messages,
                                        tools=self.available_tools,
                                        model=model
                                        )
            
                    log_agent_interaction(self.name, 'assistant_response', f"Assistant responded after tool call: {response.choices[0].message.content}")
                
                if response.choices[0].message.tool_calls is None:
                    log_agent_interaction(self.name, 'assistant_response', f"The final Assistant response is: {response.choices[0].message.content}")
                    process_query= False
                    return messages
    
    async def __process_tool_calls(self, assistant_response:ChatCompletion, messages:list[ChatCompletionMessageParam], model:str) -> list[ChatCompletionMessageParam]:
        """
        Process tool invokations from the llm 

        Parameters:

            messages (list[ChatCompletionMessageParam]): List of completion messages from groq typing
        
        Returns:
            list[ChatCompletionMessageParam]: An update list of the completion messages history
        """
        
        for choice in assistant_response.choices:
            self.logger.debug(f"[MCP_ChatBot.process_query] - Current choice: {choice}")

            # Get text content from assistant response
            response_content = choice.message.content
            messages.append({'role':'assistant', 'content':response_content})

            # Get tool use invokations from assistant response
            tool_calls = choice.message.tool_calls

            ####
            # Process each tool call
            self.logger.debug(f"Defined tool calls: {tool_calls}")
            if tool_calls is not None:
                for tool_call in tool_calls:
                    tool_name = tool_call.function.name
                    tool_args:object = json.loads(tool_call.function.arguments)
                    log_agent_interaction(self.name, 'tool_call', f"Calling tool, {tool_name} with args {tool_args}")
                
                    # Call a tool
                    session = self.tool_to_session[tool_name] 
                    # Await result of tool call
                    result = await session.call_tool(tool_name, arguments=tool_args)
                    log_agent_interaction(self.name, 'tool_call', f"Tool call results: {result.content}")


                    # Append tool call to chat history
                    messages.append(
                        {
                            "tool_call_id": tool_call.id, 
                            "role": "tool", # Indicates this message is from tool use
                            "name": tool_name,
                            "content": result.content
                        }
                    )

                # generate next response 
                response = self.groq.chat.completions.create(
                                    messages=messages,
                                    tools=self.available_tools,
                                    model=model
                                    )
        
                log_agent_interaction(self.name, 'assistant_response', f"Assistant responded after tool call: {response.choices[0].message.content}")
            
            if response.choices[0].message.tool_calls is None:
                log_agent_interaction(self.name, 'assistant_response', f"The final Assistant response is: {response.choices[0].message.content}")
                return messages

     
    async def cleanup(self): 
        """Cleanly close all resources using AsyncExitStack."""
        await self.exit_stack.aclose()


async def main():
    TEST_PROMPT="Tell me what the weather in NYC is looking like this week"
    chatbot = MCPClient()
    try:
        await chatbot.connect_to_servers()
        await chatbot.process_query(TEST_PROMPT)
    finally:
        await chatbot.cleanup()


if __name__ == "__main__":
    asyncio.run(main())

