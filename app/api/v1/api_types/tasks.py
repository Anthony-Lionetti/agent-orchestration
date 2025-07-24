from pydantic import BaseModel

class TaskPayload(BaseModel):
    queue: any
    body: any
    routing_key: any
    delivery_mode: int
    exchange: str = ""