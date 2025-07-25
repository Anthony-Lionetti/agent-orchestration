from fastapi import APIRouter
from pydantic import BaseModel
from typing import Any
from mq import MQHandler

from app.logger import setup_logging
import pika
 
# setup logger
logger = setup_logging(environment='dev')

router = APIRouter()

class TaskDefinition(BaseModel):
    prompt:str

class TaskPayload(BaseModel):
    queue: str
    body: TaskDefinition
    routing_key: str
    delivery_mode: int
    exchange: str = ""


@router.post("/submit-task")
def submit_task(payload: TaskPayload):
    # Logic to publish a message
    try:
        # Initialize MQHandler for this request
        logger.debug(f"[submit-task] - Creating RabbitMQ Connection")
        mq = MQHandler()
        conn = mq.get_connection()
        ch = conn.channel()

        # Configure Channel
        logger.debug(f"[submit-task] - Cofiguring Channel")
        ch.queue_declare(queue=payload.queue, durable=True)  # Declare queue
        ch.basic_qos(prefetch_count=1)                       # Fair dispatch

        ch.basic_publish(
            exchange=payload.exchange, 
            routing_key=payload.routing_key, 
            body=payload.body.model_dump_json(),
            properties=pika.BasicProperties(
                delivery_mode=payload.delivery_mode
            )  # Messages are now persisted
        )

        logger.info(f"[submit-task] - Published '{payload.body}' to queue '{payload.queue}'")

        # Reply to user that message is queued
        return {"status": "queued", "message": "Task successfully queued"}
    
    except Exception as e:
        print("[submit-task] - Error:", str(e))
        logger.error(f"[submit-task] - {str(e)}")
        return {"status": "failed", "message": str(e)}

    finally:
        if 'conn' in locals():
            conn.close()
            logger.debug(f"[submit-task] - Connection Cleaned Up")