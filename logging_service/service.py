import logging
import logging.config
import os
from typing import Optional, Dict, Any
from threading import Lock
from .config import LoggingConfig, LogCategory


class LoggingService:
    """
    Centralized logging service for the application.
    
    Provides a singleton interface for managing loggers across all modules.
    Handles initialization, configuration, and logger retrieval.
    """
    
    _instance: Optional['LoggingService'] = None
    _lock = Lock()
    _initialized = False
    
    def __new__(cls) -> 'LoggingService':
        """Singleton pattern implementation"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize the logging service (only once)"""
        if not self._initialized:
            self._loggers: Dict[str, logging.Logger] = {}
            self._config: Optional[Dict[str, Any]] = None
            self._environment = os.getenv('ENVIRONMENT', 'dev')
            self._initialized = True
    
    def initialize(self, environment: Optional[str] = None) -> None:
        """
        Initialize the logging configuration.
        
        Args:
            environment: Optional environment override ('dev', 'staging', 'prod')
        """
        if environment:
            self._environment = environment
        
        # Get and apply configuration
        self._config = LoggingConfig.get_config(self._environment)
        logging.config.dictConfig(self._config)
        
        # Log initialization
        system_logger = self.get_logger(LogCategory.SYSTEM)
        system_logger.info(f"Logging service initialized for environment: {self._environment}")
    
    def get_logger(self, category: LogCategory, module_name: Optional[str] = None) -> logging.Logger:
        """
        Get a logger for a specific category and module.
        
        Args:
            category: The log category (EXECUTION, AGENT, SYSTEM, AUDIT)
            module_name: Optional module name for more specific logging
            
        Returns:
            Configured logger instance
        """
        # Create logger name based on category and module
        if module_name:
            logger_name = f"{os.getenv("PROJECT_NAME")}.{category.value}.{module_name}"
        else:
            logger_name = f"{os.getenv("PROJECT_NAME")}{category.value}"
        
        # Return cached logger if exists
        if logger_name in self._loggers:
            return self._loggers[logger_name]
        
        # Create and cache new logger
        logger = logging.getLogger(logger_name)
        self._loggers[logger_name] = logger
        
        return logger
    
    def get_execution_logger(self, module_name: str) -> logging.Logger:
        """
        Convenience method for getting execution loggers.
        Use for: queue processing, database operations, API calls
        
        Args:
            module_name: Name of the module (e.g., 'publisher', 'consumer', 'database', 'api')
        """
        return self.get_logger(LogCategory.EXECUTION, module_name)
    
    def get_agent_logger(self, agent_name: str) -> logging.Logger:
        """
        Convenience method for getting agent loggers.
        Use for: LLM interactions, prompt flows, agent communications
        
        Args:
            agent_name: Name of the agent (e.g., 'chatbot', 'processor')
        """
        return self.get_logger(LogCategory.AGENT, agent_name)
    
    def get_system_logger(self, component: str = "app") -> logging.Logger:
        """
        Convenience method for getting system loggers.
        Use for: application startup, shutdown, health checks
        
        Args:
            component: Name of the system component
        """
        return self.get_logger(LogCategory.SYSTEM, component)
    
    def get_audit_logger(self, component: str = "security") -> logging.Logger:
        """
        Convenience method for getting audit loggers.
        Use for: security events, user actions, data changes
        
        Args:
            component: Name of the audited component
        """
        return self.get_logger(LogCategory.AUDIT, component)
    
    def log_startup(self, app_name: str, version: str = "unknown") -> None:
        """Log application startup"""
        logger = self.get_system_logger()
        logger.info(f"Starting {app_name} v{version}")
    
    def log_shutdown(self, app_name: str) -> None:
        """Log application shutdown"""
        logger = self.get_system_logger()
        logger.info(f"Shutting down {app_name}")
    
    def log_health_check(self, component: str, status: str, details: Optional[str] = None) -> None:
        """Log health check results"""
        logger = self.get_system_logger()
        message = f"Health check - {component}: {status}"
        if details:
            message += f" - {details}"
        logger.info(message)
    
    def flush_all_handlers(self) -> None:
        """Flush all logging handlers to ensure all logs are written"""
        for handler in logging.root.handlers:
            if hasattr(handler, 'flush'):
                handler.flush()
        
        # Also flush handlers for all our cached loggers
        for logger in self._loggers.values():
            for handler in logger.handlers:
                if hasattr(handler, 'flush'):
                    handler.flush()
    
    def get_current_environment(self) -> str:
        """Get the current logging environment"""
        return self._environment
    
    def is_initialized(self) -> bool:
        """Check if the logging service has been initialized"""
        return self._config is not None
    
    def get_log_levels(self) -> Dict[str, str]:
        """Get current log levels for all configured loggers"""
        if not self._config:
            return {}
        
        levels = {}
        for logger_name, logger_config in self._config.get('loggers', {}).items():
            levels[logger_name or 'root'] = logger_config.get('level', 'INFO')
        
        return levels


# Global instance for easy access
_logging_service = LoggingService() 