import pika
from pika import BlockingConnection
from typing import Optional
import dotenv
from logging_service import get_execution_logger, log_mq_operation
from logging_service.decorators import log_mq_operations, log_errors

dotenv.load_dotenv()
logger = get_execution_logger("publisher")

@log_mq_operations('publish')
@log_errors(logger=logger)
def publish(
        connection:BlockingConnection, 
        queue:str, 
        routing_key:str, 
        message:any, 
        content_type:Optional[str]=None, 
        delivery_mode:int=2
        ) -> None:
    """
    Publish a message to a RabbitMQ queue
    
    Parameters:
        connection (BlockingConnection): RabbitMQ blocking connection
        queue (str): Name of the queue to publish a message to
        routing_key (str): Name of the routing key for the message
        message (any): Content to publish to the broker
        content_type (Optional[str]): Optionally set the messages content type 
        delivery_mode (int): 2 for persistent, 1 for transient
    """
    # Connecting to the rabbitMQ broker
    try:
        logger.info(f"Configuring channel for queue: {queue}")
        channel = connection.channel()
        channel.basic_qos(prefetch_count=1) # mitigate slow queues and make queues available 
        channel.queue_declare(queue=queue, durable=True) # Create if one doesn't exist 

        # Publish a message to the queue
        channel.basic_publish(
            exchange="", 
            routing_key=routing_key, 
            body=message,
            properties=pika.BasicProperties(delivery_mode=delivery_mode, content_type=content_type) # Messages are now persisted
            )
        log_mq_operation("publish", queue, f"Message: {str(message)[:100]}...")
        logger.info(f"[Publisher] - Publishing message: {message}")

    except Exception as e:
        logger.error(f"Failed to publish message to queue, {queue}: {str(e)}")
        raise