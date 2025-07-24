import pika
import app.logger as logger
import dotenv
from pika import BlockingConnection
import os

dotenv.load_dotenv()
logger = logger.setup_logging(environment='dev')

class MQHandler:

    def __init__(self):
        logger.debug(f"[MQHandler] - Init")
        self.host = os.getenv("RABBITMQ_HOST")
    
    def get_connection(self) -> BlockingConnection:
        return pika.BlockingConnection(pika.ConnectionParameters(host=self.host))