from celery import Celery
from app.llm_client import MCPClient
import time

# Configure Celery to use RabbitMQ
celery_app = Celery(
    'agents',
    broker='amqp://guest:guest@rabbitmq//',
    backend='rpc://'
)

client = MCPClient()

@celery_app.task(bind=True, max_retries=3, default_retry_delay=5)
def subagent_task(self, specs: list):
    """
    Accepts a list of SubAgentTaskSpec dicts, processes them in parallel,
    and returns aggregated results.
    """
    results = []
    for spec in specs:
        try:
            # Simulate work (e.g., call an LLM or search API)

            time.sleep(1)
            results.append({
                'task_id': spec['id'],
                'objective': spec['objective'],
                'content': f"Result for {spec['objective']}"
            })
        except Exception as exc:
            raise self.retry(exc=exc)
    return results