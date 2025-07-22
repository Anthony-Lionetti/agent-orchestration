import pika
from pika.spec import BasicProperties, Basic
from pika.adapters.blocking_connection import BlockingChannel
import logger
import dotenv
import os

dotenv.load_dotenv()
logger = logger.setup_logging(environment='dev')

def process_message(body:bytes) -> None:
    print("Waiting 5 seconds")
    import time; time.sleep(5)

    # Logic for processing a message
    print(f"Processing the bytes: {body}")
    print(f"Processed into: {body.decode()}")


def main():
    # Create a RabbitMQ connection
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=os.getenv("RABBITMQ_HOST")))
    channel = connection.channel()

    channel.queue_declare(queue="task_queue", durable=True)

    # Implement fair dispatch, i.e. one consumer can only have one message at a time 
    channel.basic_qos(prefetch_count=1)


    # Define a callback to run on consumption from the queue
    def callback(ch:BlockingChannel, method:Basic.Deliver, properties:BasicProperties, body:bytes) -> None:
        logger.debug(f"[Consumer 2 Callback] - Processing")
        process_message(body)

        ch.basic_ack(delivery_tag=method.delivery_tag)
        logger.debug(f"[Consumer 2 Callback] - Acknowledged")

    # Initialize the consumption logic for the hello queue
    channel.basic_consume(queue="hello", on_message_callback=callback, auto_ack=False)
    print("Waiting for messages. To exit press CTRL+C")

    # Run consumer
    channel.start_consuming()

if __name__ == "__main__":
    main()