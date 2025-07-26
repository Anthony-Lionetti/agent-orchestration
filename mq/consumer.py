from pika.spec import BasicProperties, Basic
from pika.adapters.blocking_connection import BlockingChannel
from pika import BlockingConnection
import dotenv
from typing import Callable, TypeAlias
from logging_service import get_execution_logger, log_mq_operation
from logging_service.decorators import log_mq_operations, log_execution_time, log_errors

dotenv.load_dotenv()

logger = get_execution_logger("consumer")

MessageCallback: TypeAlias = Callable[[BlockingChannel, Basic.Deliver, BasicProperties, bytes], None]

class MessageConsumer:
    """
    Interface for consuming from rabbitmq queues

    Parameters:
        connection (BlockingConnection): RabbitMQ blocking connection
    """

    def __init__(self, connection: BlockingConnection):
        self.connection = connection
        logger.info("MessageConsumer initialized with connection")
    
    @log_mq_operations('setup')
    @log_errors(logger=logger)
    def setup(self, queue: str, callback: MessageCallback) -> BlockingChannel | None:
        """
        Sets up a channel with a queue and a callback function to process messages

        Parameters:
            queue (str): Name of the queue to consume messages from
            callback (MessageCallback): Function defining the logic for processing the message 
        """
        # Step 3: Log the setup operation start with context
        logger.info(f"Setting up consumer for queue: {queue}")
        
        try:
            channel = self.connection.channel()
            channel.queue_declare(queue=queue, durable=True)
            channel.basic_qos(prefetch_count=1)

            def logged_callback(ch: BlockingChannel, method: Basic.Deliver, properties: BasicProperties, body: bytes):
                # Log message reception with standardized format
                log_mq_operation("receive", queue, f"Message size: {len(body)} bytes, delivery_tag: {method.delivery_tag}")
                
                try:
                    # Call the original callback
                    callback(ch, method, properties, body)
                    
                    # Log successful processing
                    logger.debug(f"Message processed successfully from queue: {queue}")
                    
                except Exception as e:
                    # Log callback errors with context
                    logger.error(f"Error in message callback for queue {queue}: {str(e)}")
                    # Still ack to prevent redelivery loops in case of application errors
                    ch.basic_ack(delivery_tag=method.delivery_tag)
                    raise

            # Initialize the consumption logic with our wrapped callback
            channel.basic_consume(queue=queue, on_message_callback=logged_callback, auto_ack=False)
            
            log_mq_operation("setup", queue, "Consumer channel configured successfully")
            logger.info(f"Consumer setup completed for queue: {queue}")
            
            return channel

        except Exception as e:
            logger.error(f"Failed to setup consumer for queue {queue}: {str(e)}")
            raise

    @log_execution_time(logger=logger)
    @log_errors(logger=logger)
    def consume_channel(self, channel: BlockingChannel, queue_name: str = "unknown"):
        """
        Start consuming messages from the channel
        
        Parameters:
            channel: The configured channel to consume from
            queue_name: Optional queue name for better logging context
        """
        # Step 7: Validate input and log appropriately
        if not channel:
            logger.error("Cannot consume from None channel")
            raise ValueError("Channel cannot be None")
            
        try:
            # Log lifecycle events
            logger.info(f"Starting message consumer for queue: {queue_name}")
            log_mq_operation("start_consuming", queue_name, "Consumer started")
            
            # This will block until interrupted
            channel.start_consuming()
            
        except KeyboardInterrupt:
            # Handle graceful shutdown
            logger.info(f"Received shutdown signal for queue: {queue_name}")
            log_mq_operation("stop_consuming", queue_name, "Graceful shutdown initiated")
            channel.stop_consuming()
            logger.info(f"Consumer stopped for queue: {queue_name}")
            
        except Exception as e:
            # Handle unexpected errors
            logger.error(f"Unexpected error during consumption on queue {queue_name}: {str(e)}")
            log_mq_operation("error", queue_name, f"Consumer error: {str(e)}")
            channel.stop_consuming()
            raise


if __name__ == "__main__":
    from connection import MQHandler

    # Enhanced callback with proper logging
    @log_execution_time(logger=logger, module_name="callback")
    def consume_logic(ch: BlockingChannel, method: Basic.Deliver, properties: BasicProperties, body: bytes) -> None:
        """
        Logic to consume messages from publishers with comprehensive logging
        """
        message_content = body.decode()
        queue_name = method.routing_key  # Get queue name from delivery info
        
        logger.info(f"Processing message from queue: {queue_name}")
        log_mq_operation("process", queue_name, f"Message content preview: {message_content[:50]}...")
        
        try:
            # Simulate processing time
            print("Waiting 5 seconds")
            import time
            time.sleep(5)

            # Your actual message processing logic would go here
            print(f"Processing the bytes: {body}")
            print(f"Processed into: {message_content}")

            # Step 13: Log successful acknowledgment
            ch.basic_ack(delivery_tag=method.delivery_tag)
            log_mq_operation("ack", queue_name, f"Message acknowledged: {method.delivery_tag}")
            logger.info(f"Message successfully processed and acknowledged from queue: {queue_name}")
            
        except Exception as e:
            # Step 14: Error handling in message processing
            logger.error(f"Error processing message from queue {queue_name}: {str(e)}")
            log_mq_operation("nack", queue_name, f"Message processing failed: {str(e)}")
            
            # Decision: ACK even on error to prevent infinite redelivery
            # In production, you might want to implement dead letter queues
            ch.basic_ack(delivery_tag=method.delivery_tag)
            logger.warning(f"Message ACK'd despite error to prevent redelivery loop")
    
    # Main execution 
    queue_name = "task"  # Define queue name
    
    try:
        logger.info("Starting consumer application")
        
        # Initialize MQ connection
        mq = MQHandler()
        connection = mq.get_connection()
        logger.info("MQ connection established")
        
        # Create and setup consumer
        consumer = MessageConsumer(connection)
        ch = consumer.setup(queue_name, callback=consume_logic)
        
        if ch is None:
            logger.critical(f"Failed to setup consumer channel for queue: {queue_name}")
            exit(1)
        
        # Start consuming with queue context
        consumer.consume_channel(ch, queue_name)
        
    except Exception as e:
        logger.critical(f"Critical error in consumer application: {str(e)}")
        raise
    finally:
        # Cleanup 
        logger.info("Starting consumer cleanup")
        if 'mq' in locals():
            try:
                mq.close_connection()
                logger.info("MQ connection closed successfully")
            except Exception as e:
                logger.error(f"Error closing MQ connection: {str(e)}")
        logger.info("Consumer application shutdown complete")