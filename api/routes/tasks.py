from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Any
from mq import MQHandler, publish
from logging_service import get_execution_logger
from logging_service.decorators import log_api_endpoints, log_errors
from logging_service.utils import log_api_request
 
# setup logger
logger = get_execution_logger("api")

router = APIRouter()

class TaskDefinition(BaseModel):
    prompt:str

class TaskPayload(BaseModel):
    queue: str
    body: TaskDefinition
    routing_key: str
    delivery_mode: int
    exchange: str = ""



@router.post("/submit-task", status_code=201)
@log_api_endpoints(logger=logger)
@log_errors(logger=logger)
def submit_task(payload: TaskPayload):
    # Logic to publish a message
    logger.info(f"API call: submit_task with payload keys: {TaskDefinition.model_fields}")

    try:
        # Initialize MQHandler for this request
        mq = MQHandler()
        connection = mq.get_connection()

        # publish message to queue
        publish(
            connection=connection,
            queue=payload.queue,
            routing_key=payload.routing_key,
            message=payload.body.model_dump_json(),
            content_type="application/json"
            )

        # Reply to user that message is queued
        log_api_request("POST", "submit-task", status_code=201)
        return {"status": "queued", "message": "Task successfully queued"}
    
    except Exception as e:
        log_api_request('POST', '/submit-task', 500)
        logger.error(f"Server error in submit_task: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

    finally:
        if 'connection' in locals():
            connection.close()
            logger.debug(f"[submit-task] - Connection Cleaned Up")