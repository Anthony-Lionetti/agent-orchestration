import pika
import os
from pika import BlockingConnection
from typing import Optional

class MQHandler:
    def __init__(self):
        self.host = os.getenv("RABBITMQ_HOST", "localhost")
        self._connection: Optional[BlockingConnection] = None
    
    def get_connection(self) -> BlockingConnection:
        if self._connection is None or self._connection.is_closed:
            self._connection = pika.BlockingConnection(
                pika.ConnectionParameters(host=self.host)
            )
        return self._connection
    
    def close_connection(self):
        if self._connection and not self._connection.is_closed:
            self._connection.close() 