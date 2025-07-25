from typing import Optional, Any, Dict
from datetime import datetime
from sqlmodel import SQLModel, Field
from sqlalchemy import JSON, Column, text
import uuid
from uuid import UUID

class TaskBase(SQLModel):
    # the raw message body
    payload: Any = Field(sa_column=Column(JSON))
    # when we received it
    received_at: datetime = Field(default_factory=lambda: datetime.now())
    # optional: add more metadata if you want
    exchange: Optional[str] = None
    routing_key: Optional[str] = None

class TaskTable(TaskBase, table=True):
    __tablename__ = "tasks"
    task_id: UUID = Field(
        default_factory=uuid.uuid4,
        sa_column_kwargs={
            "primary_key": True,
            # server_default for Alembic autogenerate
            "server_default": text("gen_random_uuid()"),
            "nullable": False,
            "index": True,
        },
    )