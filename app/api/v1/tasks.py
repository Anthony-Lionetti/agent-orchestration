from fastapi import APIRouter
from pydantic import BaseModel, ValidationError
from typing import Any
from app.handlers import MQHandler
from app.logger import setup_logging
import pika
 
# setup logger
logger = setup_logging(environment='dev')

router = APIRouter()

class TaskPayload(BaseModel):
    queue: str
    body: Any
    routing_key: str
    delivery_mode: int
    exchange: str = ""


@router.post("/submit-task")
def submit_task(payload: TaskPayload):

    # Validate payload
    try:
        print("[submit-task] - Validating payload - LIVE RELOAD TEST")
        # payload.model_validate()  # This is redundant - FastAPI already validates
        logger.debug(f"[submit-task] - Payload validated")
        print("[submit-task] - Validation passed, proceeding...")
    except ValidationError as e:
        print("[submit-task] - Error Validating payload")
        return {"status": "failed", "message": f"Error: {str(e)}"}

    # Logic to publish a message
    try:
        # Initialize MQHandler for this request
        logger.debug(f"[submit-task] - Creating RabbitMQ Connection")
        print("[submit-task] - Connecting to Rabbit MQ")
        mq = MQHandler()
        print("[submit-task] - MQHandler created successfully")
        conn = mq.get_connection()
        print("[submit-task] - Connection established")
        ch = conn.channel()
        print("[submit-task] - Channel created")

        # Configure Channel
        logger.debug(f"[submit-task] - Cofiguring Channel")
        print("[submit-task] - Connecting to Rabbit MQ Channel")
        ch.queue_declare(queue=payload.queue, durable=True)  # Declare queue
        ch.basic_qos(prefetch_count=1)                       # Fair dispatch

        ch.basic_publish(
            exchange=payload.exchange, 
            routing_key=payload.routing_key, 
            body=payload.body,
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