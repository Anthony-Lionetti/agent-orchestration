# Multi-Agent Scheduling PoC

This proof-of-concept demonstrates how to schedule and orchestrate subagents using FastAPI, Celery, and RabbitMQ.

## Setup

1. Install Docker and Docker Compose.
2. Clone this repo and cd into it.
3. Run:

   ```bash
   docker-compose up --build
   ```

## How It Works

- **FastAPI App** (`/query`): Receives a text query, splits it into subagent objectives, and dispatches a Celery job.
- **Celery Worker** (`subagent_task`): Consumes messages from RabbitMQ, simulates work, and returns results.
- **Result Endpoint** (`/result/{job_id}`): Polls Celery for status and result.

## Scaling

- Increase `--concurrency` on the `worker` service to allow more parallel subagents.
- Or run multiple `worker` replicas:

  ```bash
  docker-compose up --scale worker=3
  ```

This will show how more workers decrease total processing time as tasks are parallelized.
