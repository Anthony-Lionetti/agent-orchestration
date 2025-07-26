"""
Examples of how to use the unified logging service in your RabbitMQ practice application.

This file demonstrates the proper way to integrate logging into your existing modules.
"""

# =============================================================================
# 1. Application Startup (main.py or app initialization)
# =============================================================================

def example_application_startup():
    """Example of how to initialize logging at application startup"""
    
    from logging_service import initialize_logging, log_startup
    import os
    
    # Initialize logging early in your application
    environment = os.getenv('ENVIRONMENT', 'dev')
    initialize_logging(environment)
    
    # Log application startup
    log_startup("RabbitMQ Practice App", "1.0.0")


# =============================================================================
# 2. Message Queue Operations (mq/publisher.py, mq/consumer.py)
# =============================================================================

def example_message_publisher():
    """Example of logging in message publishing operations"""
    
    from logging_service import get_execution_logger, log_mq_operation
    from logging_service.decorators import log_mq_operations, log_errors
    import pika
    
    # Get a logger for queue operations
    logger = get_execution_logger('publisher')
    
    @log_mq_operations('publish')
    @log_errors(logger=logger)
    def publish_message(connection, queue, message):
        """Publish a message with integrated logging"""
        
        # Log the start of the operation
        logger.info(f"Publishing message to queue: {queue}")
        
        try:
            channel = connection.channel()
            channel.queue_declare(queue=queue, durable=True)
            
            channel.basic_publish(
                exchange="",
                routing_key=queue,
                body=message,
                properties=pika.BasicProperties(delivery_mode=2)
            )
            
            # Use the convenience function for standardized MQ logging
            log_mq_operation('publish', queue, f"Message: {message[:100]}...")
            
            return True
            
        except Exception as e:
            # Error is automatically logged by the decorator
            logger.error(f"Failed to publish to {queue}: {str(e)}")
            raise


def example_message_consumer():
    """Example of logging in message consumption operations"""
    
    from logging_service import get_execution_logger
    from logging_service.decorators import log_mq_operations
    
    logger = get_execution_logger('consumer')
    
    @log_mq_operations('consume')
    def process_message(ch, method, properties, body):
        """Process a consumed message with logging"""
        
        message_content = body.decode()
        logger.info(f"Processing message: {message_content[:100]}...")
        
        try:
            # Your message processing logic here
            result = process_business_logic(message_content)
            
            # Acknowledge the message
            ch.basic_ack(delivery_tag=method.delivery_tag)
            logger.info("Message acknowledged successfully")
            
            return result
            
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            # Still ack to prevent redelivery loops
            ch.basic_ack(delivery_tag=method.delivery_tag)
            raise


# =============================================================================
# 3. Database Operations (database/agent_db/DAO/task_dao.py)
# =============================================================================

def example_database_operations():
    """Example of logging in database operations"""
    
    from logging_service import get_execution_logger, log_db_operation
    from logging_service.decorators import log_db_operations, log_execution_time
    from sqlalchemy.ext.asyncio import AsyncSession
    
    logger = get_execution_logger('database')
    
    class TaskDAO:
        """Enhanced Task DAO with logging"""
        
        @log_db_operations('insert', 'tasks')
        @log_execution_time(logger=logger)
        async def create_task(self, session: AsyncSession, task_data: dict):
            """Create a new task with comprehensive logging"""
            
            logger.info(f"Creating new task with data: {task_data}")
            
            try:
                # Your database insert logic here
                new_task = Task(**task_data)
                session.add(new_task)
                await session.commit()
                await session.refresh(new_task)
                
                # Use convenience function for standardized DB logging
                log_db_operation('insert', 'tasks', f"Created task ID: {new_task.id}")
                
                return new_task
                
            except Exception as e:
                await session.rollback()
                logger.error(f"Failed to create task: {str(e)}")
                raise
        
        @log_db_operations('select', 'tasks')
        async def get_task_by_id(self, session: AsyncSession, task_id: str):
            """Retrieve a task by ID with logging"""
            
            logger.debug(f"Retrieving task with ID: {task_id}")
            
            try:
                # Your database select logic here
                task = await session.get(Task, task_id)
                
                if task:
                    logger.info(f"Successfully retrieved task: {task_id}")
                else:
                    logger.warning(f"Task not found: {task_id}")
                
                return task
                
            except Exception as e:
                logger.error(f"Error retrieving task {task_id}: {str(e)}")
                raise


# =============================================================================
# 4. API Operations (api/routes/tasks.py)
# =============================================================================

def example_api_operations():
    """Example of logging in API operations"""
    
    from logging_service import get_execution_logger, log_api_request
    from logging_service.decorators import log_api_endpoints, log_execution_time
    from fastapi import APIRouter, HTTPException
    import time
    
    router = APIRouter()
    logger = get_execution_logger('api')
    
    @router.post("/submit-task")
    @log_api_endpoints(logger=logger)
    @log_execution_time(logger=logger)
    async def submit_task(payload: dict):
        """Submit a task with comprehensive API logging"""
        
        start_time = time.time()
        logger.info(f"API call: submit_task with payload keys: {list(payload.keys())}")
        
        try:
            # Your business logic here
            result = await process_task_submission(payload)
            
            # Log the successful API response
            duration_ms = (time.time() - start_time) * 1000
            log_api_request('POST', '/submit-task', 200, duration_ms)
            
            return {"status": "success", "task_id": result.id}
            
        except ValueError as e:
            # Log client errors
            duration_ms = (time.time() - start_time) * 1000
            log_api_request('POST', '/submit-task', 400, duration_ms)
            logger.warning(f"Client error in submit_task: {str(e)}")
            raise HTTPException(status_code=400, detail=str(e))
            
        except Exception as e:
            # Log server errors
            duration_ms = (time.time() - start_time) * 1000
            log_api_request('POST', '/submit-task', 500, duration_ms)
            logger.error(f"Server error in submit_task: {str(e)}")
            raise HTTPException(status_code=500, detail="Internal server error")


# =============================================================================
# 5. Agent Operations (agents/main.py, agents/client.py)
# =============================================================================

def example_agent_operations():
    """Example of logging in agent operations"""
    
    from logging_service import get_agent_logger, log_agent_interaction
    from logging_service.decorators import log_agent_actions, log_execution_time
    
    class ChatBot:
        """Enhanced ChatBot with logging"""
        
        def __init__(self, config_path: str):
            self.logger = get_agent_logger('chatbot')
            self.config_path = config_path
            self.logger.info(f"Initializing ChatBot with config: {config_path}")
        
        @log_agent_actions('chatbot', 'connection')
        async def connect_to_servers(self):
            """Connect to servers with logging"""
            
            self.logger.info("Attempting to connect to MCP servers")
            
            try:
                # Your connection logic here
                await self._establish_connections()
                self.logger.info("Successfully connected to all MCP servers")
                
            except Exception as e:
                self.logger.error(f"Failed to connect to servers: {str(e)}")
                raise
        
        @log_agent_actions('chatbot', 'processing')
        @log_execution_time()
        async def process_query(self, prompt: str):
            """Process a query with comprehensive logging"""
            
            # Log the interaction using the convenience function
            log_agent_interaction('chatbot', 'prompt_received', f"Prompt length: {len(prompt)}")
            
            try:
                # Your LLM processing logic here
                response = await self._generate_response(prompt)
                
                # Log the successful response
                log_agent_interaction('chatbot', 'response_generated', f"Response length: {len(response)}")
                
                return response
                
            except Exception as e:
                # Log the error
                log_agent_interaction('chatbot', 'error', f"Processing failed: {str(e)}")
                raise
        
        async def cleanup(self):
            """Cleanup with logging"""
            self.logger.info("Cleaning up ChatBot resources")
            # Your cleanup logic here
            self.logger.info("ChatBot cleanup completed")


# =============================================================================
# 6. System Operations (Health checks, startup, shutdown)
# =============================================================================

def example_system_operations():
    """Example of logging system operations"""
    
    from logging_service import get_system_logger, log_health_check, log_shutdown
    from logging_service.decorators import log_execution_time
    
    logger = get_system_logger('health')
    
    @log_execution_time(logger=logger)
    async def check_database_health():
        """Check database health with logging"""
        
        logger.info("Performing database health check")
        
        try:
            # Your health check logic here
            result = await ping_database()
            
            if result:
                log_health_check('database', 'healthy', 'Connection successful')
                return True
            else:
                log_health_check('database', 'unhealthy', 'Connection failed')
                return False
                
        except Exception as e:
            log_health_check('database', 'error', f"Health check failed: {str(e)}")
            return False
    
    async def graceful_shutdown():
        """Graceful shutdown with logging"""
        
        logger.info("Starting graceful shutdown")
        
        try:
            # Your shutdown logic here
            await cleanup_resources()
            log_shutdown("RabbitMQ Practice App")
            
        except Exception as e:
            logger.error(f"Error during shutdown: {str(e)}")


# =============================================================================
# 7. Audit Operations (Security, user actions)
# =============================================================================

def example_audit_operations():
    """Example of audit logging"""
    
    from logging_service import get_audit_logger
    
    audit_logger = get_audit_logger('security')
    
    def log_user_action(user_id: str, action: str, resource: str, success: bool):
        """Log user actions for audit purposes"""
        
        status = "SUCCESS" if success else "FAILURE"
        audit_logger.info(f"User: {user_id} | Action: {action} | Resource: {resource} | Status: {status}")
    
    def log_security_event(event_type: str, details: str, severity: str = "INFO"):
        """Log security events"""
        
        if severity == "CRITICAL":
            audit_logger.critical(f"SECURITY EVENT: {event_type} | Details: {details}")
        elif severity == "ERROR":
            audit_logger.error(f"SECURITY EVENT: {event_type} | Details: {details}")
        else:
            audit_logger.info(f"SECURITY EVENT: {event_type} | Details: {details}")


# =============================================================================
# Helper functions (would be in your actual business logic files)
# =============================================================================

async def process_business_logic(message_content):
    """Placeholder for message processing logic"""
    pass

async def process_task_submission(payload):
    """Placeholder for task submission logic"""
    pass

async def ping_database():
    """Placeholder for database ping logic"""
    return True

async def cleanup_resources():
    """Placeholder for resource cleanup logic"""
    pass 