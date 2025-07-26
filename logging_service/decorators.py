import time
import functools
from typing import Callable, Any, Optional
import logging
from .utils import get_execution_logger


def log_execution_time(logger: Optional[logging.Logger] = None, module_name: str = "performance"):
    """
    Decorator to log execution time of functions.
    
    Args:
        logger: Optional logger to use
        module_name: Module name for the logger if none provided
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            start_time = time.time()
            
            # Get logger
            log = logger or get_execution_logger(module_name)
            
            try:
                result = func(*args, **kwargs)
                execution_time = (time.time() - start_time) * 1000  # Convert to milliseconds
                log.info(f"Function {func.__name__} executed in {execution_time:.2f}ms")
                return result
            except Exception as e:
                execution_time = (time.time() - start_time) * 1000
                log.error(f"Function {func.__name__} failed after {execution_time:.2f}ms: {str(e)}")
                raise
                
        return wrapper
    return decorator


def log_errors(logger: Optional[logging.Logger] = None, module_name: str = "errors", reraise: bool = True):
    """
    Decorator to log errors that occur in functions.
    
    Args:
        logger: Optional logger to use
        module_name: Module name for the logger if none provided
        reraise: Whether to reraise the exception after logging
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            # Get logger
            log = logger or get_execution_logger(module_name)
            
            try:
                return func(*args, **kwargs)
            except Exception as e:
                log.error(f"Error in {func.__name__}: {str(e)}", exc_info=True)
                if reraise:
                    raise
                return None
                
        return wrapper
    return decorator


def log_function_calls(logger: Optional[logging.Logger] = None, module_name: str = "calls", log_args: bool = False):
    """
    Decorator to log function calls with optional argument logging.
    
    Args:
        logger: Optional logger to use
        module_name: Module name for the logger if none provided
        log_args: Whether to log function arguments (be careful with sensitive data)
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            # Get logger
            log = logger or get_execution_logger(module_name)
            
            if log_args:
                log.debug(f"Calling {func.__name__} with args={args}, kwargs={kwargs}")
            else:
                log.debug(f"Calling {func.__name__}")
            
            try:
                result = func(*args, **kwargs)
                log.debug(f"Successfully completed {func.__name__}")
                return result
            except Exception as e:
                log.error(f"Error in {func.__name__}: {str(e)}")
                raise
                
        return wrapper
    return decorator


def log_mq_operations(operation_type: str, logger: Optional[logging.Logger] = None):
    """
    Decorator specifically for message queue operations.
    
    Args:
        operation_type: Type of MQ operation ('publish', 'consume', 'ack', etc.)
        logger: Optional logger to use
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            # Get logger
            log = logger or get_execution_logger('queue')
            
            start_time = time.time()
            log.info(f"Starting MQ operation: {operation_type} in {func.__name__}")
            
            try:
                result = func(*args, **kwargs)
                execution_time = (time.time() - start_time) * 1000
                log.info(f"MQ operation {operation_type} completed successfully in {execution_time:.2f}ms")
                return result
            except Exception as e:
                execution_time = (time.time() - start_time) * 1000
                log.error(f"MQ operation {operation_type} failed after {execution_time:.2f}ms: {str(e)}")
                raise
                
        return wrapper
    return decorator


def log_db_operations(operation_type: str, table_name: str = "", logger: Optional[logging.Logger] = None):
    """
    Decorator specifically for database operations.
    
    Args:
        operation_type: Type of DB operation ('select', 'insert', 'update', 'delete')
        table_name: Name of the table being operated on
        logger: Optional logger to use
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            # Get logger
            log = logger or get_execution_logger('database')
            
            start_time = time.time()
            table_info = f" on table {table_name}" if table_name else ""
            log.info(f"Starting DB operation: {operation_type}{table_info} in {func.__name__}")
            
            try:
                result = func(*args, **kwargs)
                execution_time = (time.time() - start_time) * 1000
                log.info(f"DB operation {operation_type}{table_info} completed successfully in {execution_time:.2f}ms")
                return result
            except Exception as e:
                execution_time = (time.time() - start_time) * 1000
                log.error(f"DB operation {operation_type}{table_info} failed after {execution_time:.2f}ms: {str(e)}")
                raise
                
        return wrapper
    return decorator


def log_api_endpoints(logger: Optional[logging.Logger] = None):
    """
    Decorator specifically for API endpoint functions.
    
    Args:
        logger: Optional logger to use
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            # Get logger
            log = logger or get_execution_logger('api')
            
            start_time = time.time()
            log.info(f"API endpoint {func.__name__} called")
            
            try:
                result = func(*args, **kwargs)
                execution_time = (time.time() - start_time) * 1000
                log.info(f"API endpoint {func.__name__} completed successfully in {execution_time:.2f}ms")
                return result
            except Exception as e:
                execution_time = (time.time() - start_time) * 1000
                log.error(f"API endpoint {func.__name__} failed after {execution_time:.2f}ms: {str(e)}")
                raise
                
        return wrapper
    return decorator


def log_agent_actions(agent_name: str, action_type: str, logger: Optional[logging.Logger] = None):
    """
    Decorator specifically for agent actions and LLM interactions.
    
    Args:
        agent_name: Name of the agent performing the action
        action_type: Type of action ('prompt', 'response', 'processing', etc.)
        logger: Optional logger to use
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            # Import here to avoid circular imports
            from .utils import get_agent_logger
            
            # Get logger
            log = logger or get_agent_logger(agent_name)
            
            start_time = time.time()
            log.info(f"Agent {agent_name} starting action: {action_type} in {func.__name__}")
            
            try:
                result = func(*args, **kwargs)
                execution_time = (time.time() - start_time) * 1000
                log.info(f"Agent {agent_name} action {action_type} completed successfully in {execution_time:.2f}ms")
                return result
            except Exception as e:
                execution_time = (time.time() - start_time) * 1000
                log.error(f"Agent {agent_name} action {action_type} failed after {execution_time:.2f}ms: {str(e)}")
                raise
                
        return wrapper
    return decorator


def log_agent_actions_dynamic(action_type: str, logger: Optional[logging.Logger] = None, agent_name_attr: str = "name"):
    """
    Decorator specifically for agent actions that can resolve the agent name from instance attributes.
    
    Args:
        action_type: Type of action ('prompt', 'response', 'processing', etc.)
        logger: Optional logger to use
        agent_name_attr: Name of the instance attribute that contains the agent name (default: "name")
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs) -> Any:
            # Import here to avoid circular imports
            from .utils import get_agent_logger
            
            # Get agent name from instance attribute
            agent_name = getattr(self, agent_name_attr, "unknown_agent")
            
            # Get logger
            log = logger or get_agent_logger(agent_name)
            
            start_time = time.time()
            log.info(f"Agent {agent_name} starting action: {action_type} in {func.__name__}")
            
            try:
                result = func(self, *args, **kwargs)
                execution_time = (time.time() - start_time) * 1000
                log.info(f"Agent {agent_name} action {action_type} completed successfully in {execution_time:.2f}ms")
                return result
            except Exception as e:
                execution_time = (time.time() - start_time) * 1000
                log.error(f"Agent {agent_name} action {action_type} failed after {execution_time:.2f}ms: {str(e)}")
                raise
                
        return wrapper
    return decorator 