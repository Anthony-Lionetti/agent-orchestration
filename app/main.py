from fastapi import FastAPI, BackgroundTasks, HTTPException
from contextlib import asynccontextmanager
from pydantic import BaseModel
from uuid import uuid4
import os
from pathlib import Path
from app.tasks import subagent_task, celery_app
from app.llm_client import MCPClient
from logging_service import initialize_logging, log_startup, get_system_logger

initialize_logging("dev")
log_startup("API Layer", "0.0.1")
logger = get_system_logger("api")

class UserQuery(BaseModel):
    query: str

class SubAgentTaskSpec(BaseModel):
    id: str
    objective: str


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing lifespan startup")
    # Initialize Lead Orchestrator Agent
    global lead_agent
    config_path = os.getenv("LEAD_AGENT_CONFIG_PATH")
    if config_path and os.path.exists(config_path):
        logger.info(f"Config file found at: {config_path}")
    else:
        logger.error(f"Config file NOT found at: {config_path}")
    
    lead_agent = MCPClient(config_path)
    await lead_agent.connect_to_servers()
    logger.info("Lifespan initialized")
    yield
    logger.info("Clearning up lifespan startup")
    # Clean Lead Orchestrator Agent
    await lead_agent.cleanup()
    logger.info("Lifespan cleanedup")

app = FastAPI(lifespan=lifespan)

@app.post("/query")
async def submit_query(query: UserQuery, background_tasks: BackgroundTasks):
    # Decompose into subtasks
    specs = []
    for idx, term in enumerate(query.query.split()[:3]):  # simple example: one term per subagent
        specs.append(SubAgentTaskSpec(id=str(uuid4()), objective=f"Search for '{term}'"))

    # Dispatch tasks asynchronously
    job = subagent_task.delay([spec.dict() for spec in specs])

    return {"job_id": job.id, "tasks": [s.id for s in specs]}

@app.post("/simple-query")
async def submit_query(query: UserQuery):
    # run a simple query
    try:
        result = await lead_agent.process_query(query.query)
        return {"results": result}
    except HTTPException as e:
        logger.error(f"Error calling llm client: {str(e)}")
        raise

@app.get("/result/{job_id}")
async def get_result(job_id: str):
    res = celery_app.AsyncResult(job_id)
    if res.ready():
        return {"status": res.status, "result": res.get()}
    return {"status": res.status}