## Building the initial agent!
import asyncio
from client import MCP_ChatBot
from mq import MessageConsumer, MQHandler
from mq.consumer import BlockingChannel, Basic, BasicProperties
import json


async def main():
    mq = MQHandler()
    connection = mq.get_connection()
    consumer = MessageConsumer(connection=connection)

    chatbot = MCP_ChatBot("/Users/ant-lion/Desktop/Dev-learning/rabbitmq-practice/agents/server_config.json")
    try:
        await chatbot.connect_to_servers()

    except Exception as e:
        print("Error with MCP:",str(e))

    async def process_message(ch:BlockingChannel, method:Basic.Deliver, properties:BasicProperties, body:bytes):
        # decode json message and parse out prompt
        message_raw = body.decode()
        message_json = json.loads(message_raw)
        print(f"Message is: {message_json["prompt"]}")

        await chatbot.process_query(message_json["prompt"])

        # ack 
        ch.basic_ack(delivery_tag=method.delivery_tag)


    ch = consumer.setup("task", callback=process_message)

    try:
        consumer.consume_channel(ch)

    except Exception as e:
        print("Error Consuming:", str(e))


    finally:
        await chatbot.cleanup()
        if 'mq' in locals():  # Check if exisits first
            mq.close_connection()


if __name__ == "__main__":
    asyncio.run(main())
    