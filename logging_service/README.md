# Unified Logging Service

A centralized logging service for the RabbitMQ practice application, designed to eliminate code duplication and provide consistent logging across all modules.

## Overview

This unified logging service replaces the duplicate `logger.py` files across your modules (`agents/`, `api/`, `mq/`) with a single, configurable, and extensible logging system.

### Key Features

- **Centralized Configuration**: Single source of truth for all logging configuration
- **Category-Based Logging**: Separate log categories for different types of operations
- **Environment-Aware**: Different configurations for dev, staging, and production
- **Structured Logging**: JSON formatting support for production environments
- **Performance Monitoring**: Built-in execution time tracking
- **Error Handling**: Comprehensive error logging with decorators
- **Log Rotation**: Automatic log file rotation to manage disk space
- **Audit Trail**: Dedicated audit logging for security and compliance

## Log Categories

The service organizes logs into four main categories:

### 1. Execution Logs (`execution.log`)

For operational activities:

- Queue processing (publish/consume)
- Database operations (CRUD)
- API calls and responses
- General application flow

### 2. Agent Logs (`agent.log`)

For AI/LLM interactions:

- Prompt processing
- Model responses
- Agent communications
- LLM performance metrics

### 3. System Logs (`system.log`)

For system-level operations:

- Application startup/shutdown
- Health checks
- Configuration changes
- Resource management

### 4. Audit Logs (`audit.log`)

For security and compliance:

- User actions
- Security events
- Data access
- Administrative operations

## Quick Start

### 1. Initialize Logging in Your Application

```python
# In your main.py or application startup
from logging_service import initialize_logging, log_startup

# Initialize logging early in your application
initialize_logging('dev')  # or 'staging', 'prod'

# Log application startup
log_startup("RabbitMQ Practice App", "1.0.0")
```

### 2. Get Loggers in Your Modules

```python
# For queue operations
from logging_service import get_execution_logger
logger = get_execution_logger('publisher')
logger.info("Publishing message to queue")

# For agent operations
from logging_service import get_agent_logger
logger = get_agent_logger('chatbot')
logger.info("Processing user prompt")

# For database operations
from logging_service import get_execution_logger
logger = get_execution_logger('database')
logger.info("Executing database query")
```

### 3. Use Decorators for Automatic Logging

```python
from logging_service.decorators import log_execution_time, log_mq_operations

@log_mq_operations('publish')
@log_execution_time()
def publish_message(queue, message):
    # Your code here - timing and MQ operations are logged automatically
    pass
```

## Migration from Existing Logger Files

### Current State

```
agents/logger.py    (274 lines - duplicated)
api/logger.py       (274 lines - duplicated)
mq/logger.py        (274 lines - duplicated)
```

### After Migration

```
logging_service/
├── __init__.py     (exports)
├── config.py       (centralized configuration)
├── service.py      (main service class)
├── utils.py        (utility functions)
├── decorators.py   (logging decorators)
└── examples.py     (usage examples)
```

### Migration Steps

1. **Replace existing imports**:

   ```python
   # OLD
   from mq.logger import setup_logging
   logger = setup_logging(environment='dev')

   # NEW
   from logging_service import get_execution_logger
   logger = get_execution_logger('queue')
   ```

2. **Initialize logging once at startup**:

   ```python
   # Add to your main.py
   from logging_service import initialize_logging
   initialize_logging('dev')
   ```

3. **Update your modules** (see examples below)

## Usage Examples

### Message Queue Operations

```python
# mq/publisher.py
from logging_service import get_execution_logger, log_mq_operation
from logging_service.decorators import log_mq_operations

logger = get_execution_logger('publisher')

@log_mq_operations('publish')
def publish(connection, queue, message):
    logger.info(f"Publishing to queue: {queue}")

    try:
        # Your publishing logic
        channel.basic_publish(...)
        log_mq_operation('publish', queue, f"Message: {message[:100]}")

    except Exception as e:
        logger.error(f"Failed to publish: {str(e)}")
        raise
```

### Database Operations

```python
# database/agent_db/DAO/task_dao.py
from logging_service import get_execution_logger
from logging_service.decorators import log_db_operations

logger = get_execution_logger('database')

class TaskDAO:
    @log_db_operations('insert', 'tasks')
    async def create_task(self, session, task_data):
        logger.info(f"Creating task: {task_data}")
        # Your database logic
```

### API Operations

```python
# api/routes/tasks.py
from logging_service import get_execution_logger
from logging_service.decorators import log_api_endpoints

logger = get_execution_logger('api')

@router.post("/submit-task")
@log_api_endpoints()
async def submit_task(payload):
    logger.info(f"Task submission: {payload}")
    # Your API logic
```

### Agent Operations

```python
# agents/main.py
from logging_service import get_agent_logger, log_agent_interaction
from logging_service.decorators import log_agent_actions

class ChatBot:
    def __init__(self):
        self.logger = get_agent_logger('chatbot')

    @log_agent_actions('chatbot', 'processing')
    async def process_query(self, prompt):
        log_agent_interaction('chatbot', 'prompt_received', f"Length: {len(prompt)}")
        # Your agent logic
```

## Environment Configuration

### Development Environment

- Verbose console output with DEBUG level
- Detailed file logging
- Debug file with all operations
- Fast rotation for testing

### Staging Environment

- JSON formatting for structured logging
- Moderate verbosity
- Performance monitoring
- Real-world testing setup

### Production Environment

- JSON formatting for log aggregation
- Minimal console output (WARNING+ only)
- Email alerts for CRITICAL errors
- Long retention periods
- Optimized for performance

## Log File Structure

```
logs/
├── execution.log       # Queue, DB, API operations
├── agent.log          # LLM and agent interactions
├── system.log         # Startup, health, system events
├── audit.log          # Security and compliance events
├── errors.log         # All errors across components
└── debug.log          # Debug information (dev only)
```

## Performance Features

- **Lazy Initialization**: Loggers are created only when needed
- **Singleton Pattern**: Single service instance across the application
- **Thread-Safe**: Safe for concurrent operations
- **Log Rotation**: Automatic file rotation prevents disk space issues
- **Buffered Writing**: Efficient I/O operations

## Best Practices

1. **Initialize Early**: Call `initialize_logging()` at application startup
2. **Use Categories**: Choose the right log category for your operations
3. **Use Decorators**: Leverage decorators for consistent logging patterns
4. **Avoid Sensitive Data**: Don't log passwords, tokens, or PII
5. **Use Appropriate Levels**: DEBUG for development, INFO for operations, ERROR for problems
6. **Flush on Shutdown**: Call `flush_all_handlers()` during graceful shutdown

## Configuration

### Environment Variables

```bash
# Set the environment
export ENVIRONMENT=dev|staging|prod

# Production email configuration (optional)
export SMTP_HOST=smtp.example.com
export LOG_FROM_EMAIL=noreply@example.com
export LOG_TO_EMAIL=admin@example.com
```

### Custom Configuration

You can extend the configuration by modifying `LoggingConfig` class:

```python
from logging_service.config import LoggingConfig

# Extend base configuration
config = LoggingConfig.get_config('prod')
config['handlers']['custom_handler'] = {
    # Your custom handler configuration
}
```

## Monitoring and Alerting

### Log Aggregation

- Production uses JSON formatting for easy parsing
- Compatible with ELK stack, Fluentd, or other log aggregators
- Structured fields for filtering and searching

### Error Alerting

- Critical errors automatically send email alerts in production
- Error logs are separated for easy monitoring
- Audit logs provide security event tracking

## Troubleshooting

### Common Issues

1. **"Logging not initialized"**

   - Solution: Call `initialize_logging()` early in your application

2. **"No handlers found"**

   - Solution: Ensure you're using the correct logger category

3. **"Log files not created"**

   - Solution: Check that the `logs/` directory exists and is writable

4. **"Performance degradation"**
   - Solution: Reduce log level in production, ensure log rotation is working

### Debug Mode

Enable debug logging to troubleshoot issues:

```python
initialize_logging('dev')  # Enables debug file logging
```

## Migration Checklist

- [ ] Create `logging_service/` directory
- [ ] Copy all service files
- [ ] Initialize logging in main application files
- [ ] Update `mq/publisher.py` imports and logging calls
- [ ] Update `mq/consumer.py` imports and logging calls
- [ ] Update `api/routes/tasks.py` imports and logging calls
- [ ] Update `agents/main.py` to use agent logging
- [ ] Implement database DAO logging
- [ ] Test all log categories in development
- [ ] Remove old `logger.py` files
- [ ] Update environment configuration
- [ ] Test production configuration

## Future Enhancements

- **Metrics Integration**: Add metrics collection alongside logging
- **Log Streaming**: Real-time log streaming for monitoring
- **Custom Formatters**: Domain-specific log formatting
- **Log Analytics**: Built-in log analysis and reporting
- **Integration APIs**: REST API for log management
