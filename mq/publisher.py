import pika
from pika import BlockingConnection
from mq.logger import logger
from typing import Optional
import dotenv

dotenv.load_dotenv()
logger = logger.setup_logging(environment='dev')


def publish(
        connection:BlockingConnection, 
        queue:str, 
        message:any, 
        content_type:Optional[str]=None, 
        delivery_mode:int=2
        ) -> None:
    """
    Publish a message to a RabbitMQ queue
    
    Parameters:
        connection (BlockingConnection): RabbitMQ blocking connection
        queue (str): Name of the queue to publish a message to
        message (any): Content to publish to the broker
        content_type (Optional[str]): Optionally set the messages content type 
        delivery_mode (int): 2 for persistent, 1 for transient
    """
    # Connecting to the rabbitMQ broker
    try:
        logger.info(f"[Publisher] - Configuring Channel")
        channel = connection.channel()
        channel.basic_qos(prefetch_count=1) # mitigate slow queues and make queues available 
        channel.queue_declare(queue=queue, durable=True) # Create if one doesn't exist 

        # Publish a message to the queue
        channel.basic_publish(
            exchange="", 
            routing_key=queue, 
            body=message,
            properties=pika.BasicProperties(delivery_mode=delivery_mode, content_type=content_type) # Messages are now persisted
            )
        logger.info(f"[Publisher] - Publishing message: {message}")

    except Exception as e:
        logger.error(f"[Publisher] - Error: {str(e)}")