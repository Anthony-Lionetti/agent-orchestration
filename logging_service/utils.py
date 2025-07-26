import logging
import os
from typing import Optional
from .service import _logging_service
from .config import LogCategory


def initialize_logging(environment: Optional[str] = None) -> None:
    """
    Initialize the logging service. Call this early in your application startup.
    
    Args:
        environment: Optional environment override ('dev', 'staging', 'prod')
    """
    env = environment or os.getenv('ENVIRONMENT', 'dev')
    _logging_service.initialize(env)


def get_logger(category: LogCategory, module_name: Optional[str] = None) -> logging.Logger:
    """
    Get a logger for a specific category and module.
    
    Args:
        category: The log category (EXECUTION, AGENT, SYSTEM, AUDIT)
        module_name: Optional module name for more specific logging
        
    Returns:
        Configured logger instance
    """
    return _logging_service.get_logger(category, module_name)


def get_execution_logger(module_name: str) -> logging.Logger:
    """
    Get an execution logger for a specific module.
    Use for: queue processing, database operations, API calls
    
    Args:
        module_name: Name of the module (e.g., 'publisher', 'consumer', 'database', 'api')
    """
    return _logging_service.get_execution_logger(module_name)


def get_agent_logger(agent_name: str) -> logging.Logger:
    """
    Get an agent logger for a specific agent.
    Use for: LLM interactions, prompt flows, agent communications
    
    Args:
        agent_name: Name of the agent (e.g., 'chatbot', 'processor')
    """
    return _logging_service.get_agent_logger(agent_name)


def get_system_logger(component: str = "app") -> logging.Logger:
    """
    Get a system logger for a specific component.
    Use for: application startup, shutdown, health checks
    
    Args:
        component: Name of the system component
    """
    return _logging_service.get_system_logger(component)


def get_audit_logger(component: str = "security") -> logging.Logger:
    """
    Get an audit logger for a specific component.
    Use for: security events, user actions, data changes
    
    Args:
        component: Name of the audited component
    """
    return _logging_service.get_audit_logger(component)


def log_startup(app_name: str, version: str = "unknown") -> None:
    """Log application startup"""
    _logging_service.log_startup(app_name, version)


def log_shutdown(app_name: str) -> None:
    """Log application shutdown"""
    _logging_service.log_shutdown(app_name)


def log_health_check(component: str, status: str, details: Optional[str] = None) -> None:
    """Log health check results"""
    _logging_service.log_health_check(component, status, details)


def flush_all_handlers() -> None:
    """Flush all logging handlers to ensure all logs are written"""
    _logging_service.flush_all_handlers()


def get_current_environment() -> str:
    """Get the current logging environment"""
    return _logging_service.get_current_environment()


def is_logging_initialized() -> bool:
    """Check if the logging service has been initialized"""
    return _logging_service.is_initialized()


# Convenience functions for common logging patterns
def log_mq_operation(operation: str, queue: str, message: str, logger: Optional[logging.Logger] = None) -> None:
    """
    Log a message queue operation with standardized format.
    
    Args:
        operation: The operation being performed (e.g., 'publish', 'consume', 'ack')
        queue: The queue name
        message: Additional message or payload info
        logger: Optional logger to use, defaults to queue logger
    """
    if logger is None:
        logger = get_execution_logger('queue')
    
    logger.info(f"MQ Operation: {operation} | Queue: {queue} | Details: {message}")


def log_db_operation(operation: str, table: str, details: str, logger: Optional[logging.Logger] = None) -> None:
    """
    Log a database operation with standardized format.
    
    Args:
        operation: The operation being performed (e.g., 'insert', 'update', 'select')
        table: The table name
        details: Additional details about the operation
        logger: Optional logger to use, defaults to database logger
    """
    if logger is None:
        logger = get_execution_logger('database')
    
    logger.info(f"DB Operation: {operation} | Table: {table} | Details: {details}")


def log_api_request(method: str, endpoint: str, status_code: int, duration_ms: float = None, logger: Optional[logging.Logger] = None) -> None:
    """
    Log an API request with standardized format.
    
    Args:
        method: HTTP method (GET, POST, etc.)
        endpoint: The API endpoint
        status_code: HTTP status code
        duration_ms: Optional request duration in milliseconds
        logger: Optional logger to use, defaults to api logger
    """
    if logger is None:
        logger = get_execution_logger('api')
    
    message = f"API Request: {method} {endpoint} | Status: {status_code}"
    if duration_ms is not None:
        message += f" | Duration: {duration_ms:.2f}ms"
    
    logger.info(message)


def log_agent_interaction(agent_name: str, interaction_type: str, details: str, logger: Optional[logging.Logger] = None) -> None:
    """
    Log an agent interaction with standardized format.
    
    Args:
        agent_name: Name of the agent
        interaction_type: Type of interaction (e.g., 'prompt', 'response', 'error')
        details: Additional details about the interaction
        logger: Optional logger to use, defaults to agent logger
    """
    if logger is None:
        logger = get_agent_logger(agent_name)
    
    logger.info(f"Agent Interaction: {agent_name} | Type: {interaction_type} | Details: {details}") 