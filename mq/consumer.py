from pika.spec import BasicProperties, Basic
from pika.adapters.blocking_connection import BlockingChannel
from pika import BlockingConnection
import dotenv
from mq.logger import setup_logging
from typing import Callable, TypeAlias

dotenv.load_dotenv()
logger = setup_logging(environment='dev')

MessageCallback: TypeAlias = Callable[[BlockingChannel, Basic.Deliver, BasicProperties, bytes], None]

class MessageConsumer:
    """
    Interface for consuming from rabbitmq queues

    Parameters:
        connection (BlockingConnection): RabbitMQ blocking connection
    """

    def __init__(self, connection:BlockingConnection):
        self.connection = connection
    
    def setup(self, queue: str, callback: MessageCallback) -> BlockingChannel | None:
        """
        Sets up a channel with a queue and a callback function to process messages

        Paramaters:
            queue (str): Name of the queue to consume messages from

            callback (callable): Function defining the logic for processing the message 
                Parameters:
                    ch (BlockingChannel): Consumer Channel
                    method (Basic.Deliver): Used to ack the message once processed 
                    properties (BasicProperties): RabbitMQ properties
                    body (bytes): Contnent of from the queue to process

        """
        try:
            channel = self.connection.channel()
            channel.queue_declare(queue=queue, durable=True) # Declare the queue 
            channel.basic_qos(prefetch_count=1) # One consumer can only have one message at a time 

            # Initialize the consumption logic for the task_queue (fixed queue name)
            channel.basic_consume(queue=queue, on_message_callback=callback, auto_ack=False)

            return channel

        except Exception as e:
            logger.error(f"[init_consumer] - Error configuring channel: {str(e)}")
            return None


    def consume_channel(self, channel: BlockingChannel):
        """Start consuming messages from the channel"""
        if not channel:
            logger.error("Cannot consume from None channel")
            return
            
        try:
            logger.info("Starting consumer...")
            channel.start_consuming()
        except KeyboardInterrupt:
            logger.info("Stopping consumer...")
            channel.stop_consuming()
        except Exception as e:
            logger.error(f"Error during consumption: {str(e)}")
            channel.stop_consuming()
            raise
    
        


if __name__ == "__main__":
    from connection import MQHandler

    def consume_logic(ch:BlockingChannel, method:Basic.Deliver, properties:BasicProperties, body:bytes) -> None:
        """
        Logic to consume messages from publishers
        """
        logger.debug(f"[Consumer Callback] - Processing")
        print("Waiting 5 seconds")
        import time; time.sleep(5)

        # Logic for processing a message
        print(f"Processing the bytes: {body}")
        print(f"Processed into: {body.decode()}")

        ch.basic_ack(delivery_tag=method.delivery_tag)
        logger.debug(f"[Consumer Callback] - Acknowledged")
    
    try:
        mq = MQHandler()
        connection = mq.get_connection()
        consumer = MessageConsumer(connection)

        ch = consumer.setup("task", callback=consume_logic)
        if ch is None:  # Add this check!
            logger.error("Failed to setup consumer channel")
            exit(1)
        
        consumer.consume_channel(ch)
    except Exception as e:
        logger.error(f"Consumer error: {str(e)}")
    finally:
        # This will fail if mq wasn't created successfully
        if 'mq' in locals():  # Add this check
            mq.close_connection()