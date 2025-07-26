## Building the initial agent!
import asyncio
from client import MCPClient
from mq import MessageConsumer, MQHandler
from mq.consumer import BlockingChannel, Basic, BasicProperties
from logging_service import initialize_logging, log_startup
import json
import concurrent.futures
# import threading

QUEUE_NAME="chatbot"

initialize_logging("dev")
log_startup("Agent Worker", "0.0.1")


async def main():
    mq = MQHandler()
    connection = mq.get_connection()
    consumer = MessageConsumer(connection=connection)

    chatbot = MCPClient("/Users/ant-lion/Desktop/Dev-learning/rabbitmq-practice/agents/server_config.json")
    try:
        await chatbot.connect_to_servers()

    except Exception as e:
        print("Error with MCP:",str(e))

    # Create a thread pool executor for running async tasks
    executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)

    def process_message(ch:BlockingChannel, method:Basic.Deliver, properties:BasicProperties, body:bytes):
        # decode json message and parse out prompt
        message_raw = body.decode()
        message_json = json.loads(message_raw)
        print(f"Message is: {message_json['prompt']}")

        def run_async_in_thread():
            """Run the async chatbot processing in a separate thread with its own event loop"""
            try:
                # Create a new event loop for this thread
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                # Run the async function
                result = loop.run_until_complete(chatbot.process_query(message_json["prompt"]))
                loop.close()
                return result
                
            except Exception as e:
                print(f"Error in async processing: {str(e)}")
                raise

        try:
            # Submit the async task to the thread pool
            future = executor.submit(run_async_in_thread)
            
            # Wait for completion
            future.result()
            
            # ack 
            ch.basic_ack(delivery_tag=method.delivery_tag)
            print("ACK-ing Message\n\n")
            
        except Exception as e:
            print(f"Error processing message: {str(e)}")
            # Still ack the message to prevent redelivery loops
            ch.basic_ack(delivery_tag=method.delivery_tag)


    ch = consumer.setup(QUEUE_NAME, callback=process_message)

    try:
        consumer.consume_channel(ch)

    except Exception as e:
        print("Error Consuming:", str(e))

    finally:
        executor.shutdown(wait=True)  # Clean up the thread pool
        await chatbot.cleanup()
        if 'mq' in locals():  # Check if exisits first
            mq.close_connection()


if __name__ == "__main__":
    asyncio.run(main())
    