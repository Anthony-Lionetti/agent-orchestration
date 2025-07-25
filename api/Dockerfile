# Development Dockerfile with uv
FROM python:3.12-slim-bookworm

# Copy uv from official image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/src

WORKDIR /src

# Copy workspace files first (for better caching)
COPY pyproject.toml uv.lock ./

# Install dependencies
RUN --mount=type=cache,target=/root/.cache uv sync --locked

# Copy application code
COPY ./api ./api
COPY ./database ./database
COPY ./mq ./mq

# Create non-root user
RUN adduser --disabled-password --gecos '' --shell /bin/bash user \
    && chown -R user:user /src

USER user

# Expose port
EXPOSE 8000

# Use uv run with reload for development
CMD ["uv", "run", "uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]