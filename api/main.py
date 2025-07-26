from fastapi import FastAPI
from api.routes.tasks import router as task_router
from fastapi.middleware.cors import CORSMiddleware
from api.core.config import settings
from logging_service import initialize_logging, log_startup

initialize_logging("dev")
log_startup("RabbitMQ API Layer", "0.0.1")


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION
)

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(task_router, prefix="/api/tasks", tags=["tasks"])

@app.get("/")
async def health_check():
    return {"status": "ok", "version": settings.VERSION}
