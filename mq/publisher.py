import pika
import app.logger as logger
import dotenv
import os

dotenv.load_dotenv()
logger = logger.setup_logging(environment='dev')


def main():
    # Connecting to the rabbitMQ broker
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=os.getenv("RABBITMQ_HOST")))
    logger.debug(f"[Publisher] - Connection: {str(connection)}")
    channel = connection.channel()
    logger.debug(f"[Publisher] - Channel: {str(channel)}")

    # Using prefetch to mitigate slow queues and make queues available 
    channel.basic_qos(prefetch_count=1)

    # Create a queue and ensure the queue exists, if not create one
    channel.queue_declare(queue="task_queue", durable=True)

    for message in ["Hello 1", "Hello 2",  "Hello 3", "Hello 4", "Hello 5"]:
        # Message to publish
        # Publish a message to the queue
        channel.basic_publish(
            exchange="", 
            routing_key="hello", 
            body=message,
            properties=pika.BasicProperties(delivery_mode=2) # Messages are now persisted

            )

    # Cleanup / close connection
    connection.close()


if __name__ == "__main__":
    main()
