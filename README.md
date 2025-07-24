# Agentic AI Messaging System (Work in Progress)

A template project demonstrating how to build an agentic AI messaging system using RabbitMQ, Python (FastAPI & Celery), Docker, and PostgreSQL.

This repository provides a step-by-step tutorial and working code to:

- Set up RabbitMQ with management UI in Docker
- Write Python producers and consumers using Pika
- Implement reliable work queues with acknowledgments and durability
- Integrate RabbitMQ with a FastAPI application for asynchronous task handling
- Use Celery as a task queue library with RabbitMQ as the broker and PostgreSQL as the result backend
- Orchestrate all services with Docker Compose for easy development and testing

---

## 🚀 Features

- **Modular Architecture**: Decoupled producers, consumers, and web API
- **Reliability**: Durable queues, message persistence, manual acknowledgments
- **Scalability**: Multiple worker processes, prefetch for fair dispatch
- **Observability**: RabbitMQ management console & Celery monitoring
- **Containerized**: All components run in Docker containers via Docker Compose

---

## 📋 Prerequisites

- Docker & Docker Compose
- Python 3.8+
- `uv` for Python dependencies

---

## 🛠 Installation & Setup

1. **Clone the repository**

   ```bash
   git clone https://github.com/Anthony-Lionetti/agent-orchestration.git
   cd agent-orchestration
   ```

2. **Build and start all services**

   ```bash
   docker-compose up --build -d
   ```

3. **Verify services**

   - RabbitMQ UI: [http://localhost:15672](http://localhost:15672) (default credentials `guest`/`guest`)
   - FastAPI docs: [http://localhost:8000/docs](http://localhost:8000/docs)
   - PostgreSQL: `localhost:5432` (credentials in `docker-compose.yml`)

4. **Run example task**

   ```bash
   curl -X POST \
     -H "Content-Type: application/json" \
     -d '{"a":5,"b":7}' \
     http://localhost:8000/add
   ```

---

## 🔧 Usage (Work in Progress)

### FastAPI Endpoints

- **`POST /add`**: Submit a task (adds two numbers asynchronously). Returns a `task_id`.
- **`GET /task-result/{task_id}`**: Retrieve the status and result of a submitted task.

<!-- ### Celery Worker

- Starts automatically via Docker Compose.
- Processes tasks defined in `celery_tasks.py`.
- Stores results in PostgreSQL. -->

---

<!-- ## 📂 Project Structure

```
├── docker-compose.yml      # Orchestrates all services
├── Dockerfile.app          # Builds FastAPI application image
├── Dockerfile.celery       # Builds Celery worker image
├── app/                    # FastAPI application code
│   ├── main.py             # FastAPI routes
│   └── celery_tasks.py     # Celery configuration & task definitions
└── scripts/                # Utility scripts (producer.py, consumer.py)
```

---
-->

## 📜 License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
