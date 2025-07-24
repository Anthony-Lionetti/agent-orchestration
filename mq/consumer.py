import pika
from pika.spec import BasicProperties, Basic
from pika.adapters.blocking_connection import BlockingChannel
import dotenv
from logger import setup_logging
import os

dotenv.load_dotenv()
logger = setup_logging(environment='dev')

def process_message(body:bytes) -> None:
    print("Waiting 5 seconds")
    import time; time.sleep(5)

    # Logic for processing a message
    print(f"Processing the bytes: {body}")
    print(f"Processed into: {body.decode()}")


def main():
    # Create a RabbitMQ connection
    rabbitmq_host = os.getenv("RABBITMQ_HOST", "localhost")
    rabbitmq_port = int(os.getenv("RABBITMQ_PORT", "5672"))
    rabbitmq_user = os.getenv("RABBITMQ_USER", "guest")
    rabbitmq_password = os.getenv("RABBITMQ_PASSWORD", "guest")
    
    credentials = pika.PlainCredentials(rabbitmq_user, rabbitmq_password)
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host=rabbitmq_host,
            port=rabbitmq_port,
            credentials=credentials
        )
    )
    channel = connection.channel()

    # Declare the queue (make sure it matches the publisher)
    channel.queue_declare(queue="task", durable=True)

    # Implement fair dispatch, i.e. one consumer can only have one message at a time 
    channel.basic_qos(prefetch_count=1)

    # Define a callback to run on consumption from the queue
    def callback(ch:BlockingChannel, method:Basic.Deliver, properties:BasicProperties, body:bytes) -> None:
        logger.debug(f"[Consumer Callback] - Processing")
        process_message(body)

        ch.basic_ack(delivery_tag=method.delivery_tag)
        logger.debug(f"[Consumer Callback] - Acknowledged")

    # Initialize the consumption logic for the task_queue (fixed queue name)
    channel.basic_consume(queue="task", on_message_callback=callback, auto_ack=False)
    print("Waiting for messages. To exit press CTRL+C")

    try:
        # Run consumer
        channel.start_consuming()
    except KeyboardInterrupt:
        print("Stopping consumer...")
        channel.stop_consuming()
        connection.close()

if __name__ == "__main__":
    main()