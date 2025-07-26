import logging.config
import os
from pathlib import Path
from typing import Dict, Any
from enum import Enum

# Ensure logs directory exists
Path("logs").mkdir(exist_ok=True)

class LogLevel(Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

class LogCategory(Enum):
    """Different categories of logs for the application"""
    EXECUTION = "execution"  # Queue processing, DB access, API calls
    AGENT = "agent"          # LLM interactions, prompt flows (future)
    SYSTEM = "system"        # Application startup, shutdown, health
    AUDIT = "audit"          # Security, user actions, data changes

class LogEnv(Enum):
    """Different categories of logs for the application"""
    DEV = "dev"  # Queue processing, DB access, API calls
    STAGING = "staging"          # LLM interactions, prompt flows (future)
    PROD = "prod"        # Application startup, shutdown, health

class LoggingConfig:
    """Centralized logging configuration for the RabbitMQ practice application"""
    
    @staticmethod
    def get_config(environment: LogEnv = LogEnv.DEV) -> Dict[str, Any]:
        """
        Get logging configuration based on environment
        
        Args:
            environment: 'dev', 'staging', 'prod'
        """
        base_config = LoggingConfig._get_base_config()
        
        if environment == LogEnv.DEV:
            return LoggingConfig._enhance_for_production(base_config)
        elif environment == LogEnv.STAGING:
            return LoggingConfig._enhance_for_staging(base_config)
        else:
            return LoggingConfig._enhance_for_development(base_config)
    
    @staticmethod
    def _get_base_config() -> Dict[str, Any]:
        """Base configuration shared across all environments"""
        return {
            'version': 1,
            'disable_existing_loggers': False,
            
            'formatters': {
                'detailed': {
                    'format': '%(asctime)s - %(name)s - %(levelname)s - %(module)s - %(funcName)s:%(lineno)d - %(message)s',
                    'datefmt': '%Y-%m-%d %H:%M:%S'
                },
                'simple': {
                    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    'datefmt': '%Y-%m-%d %H:%M:%S'
                },
                'json': {
                    'class': 'pythonjsonlogger.jsonlogger.JsonFormatter',
                    'format': '%(asctime)s %(name)s %(levelname)s %(module)s %(funcName)s %(lineno)d %(message)s'
                },
                'execution': {
                    'format': '[EXEC] %(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    'datefmt': '%Y-%m-%d %H:%M:%S'
                },
                'agent': {
                    'format': '[AGENT] %(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    'datefmt': '%Y-%m-%d %H:%M:%S'
                },
                'audit': {
                    'format': '[AUDIT] %(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    'datefmt': '%Y-%m-%d %H:%M:%S'
                }
            },
            
            'handlers': {
                'console': {
                    'class': 'logging.StreamHandler',
                    'level': 'INFO',
                    'formatter': 'simple',
                    'stream': 'ext://sys.stdout'
                },
                'console_error': {
                    'class': 'logging.StreamHandler',
                    'level': 'ERROR', 
                    'formatter': 'detailed',
                    'stream': 'ext://sys.stderr'
                },
                
                # Execution logs (queue, db, api operations)
                'execution_file': {
                    'class': 'logging.handlers.RotatingFileHandler',
                    'level': 'INFO',
                    'formatter': 'execution',
                    'filename': 'logs/execution.log',
                    'maxBytes': 10485760,  # 10MB
                    'backupCount': 5,
                    'encoding': 'utf-8'
                },
                
                # Agent/LLM interaction logs
                'agent_file': {
                    'class': 'logging.handlers.RotatingFileHandler',
                    'level': 'INFO',
                    'formatter': 'agent',
                    'filename': 'logs/agent.log',
                    'maxBytes': 10485760,  # 10MB
                    'backupCount': 5,
                    'encoding': 'utf-8'
                },
                
                # System logs (startup, shutdown, health)
                'system_file': {
                    'class': 'logging.handlers.RotatingFileHandler',
                    'level': 'INFO',
                    'formatter': 'detailed',
                    'filename': 'logs/system.log',
                    'maxBytes': 5242880,  # 5MB
                    'backupCount': 3,
                    'encoding': 'utf-8'
                },
                
                # Error logs (all errors across all components)
                'error_file': {
                    'class': 'logging.handlers.RotatingFileHandler',
                    'level': 'ERROR',
                    'formatter': 'detailed',
                    'filename': 'logs/errors.log',
                    'maxBytes': 10485760,  # 10MB
                    'backupCount': 10,
                    'encoding': 'utf-8'
                },
                
                # Audit logs (security, user actions)
                'audit_file': {
                    'class': 'logging.handlers.RotatingFileHandler',
                    'level': 'INFO',
                    'formatter': 'audit',
                    'filename': 'logs/audit.log',
                    'maxBytes': 20971520,  # 20MB
                    'backupCount': 10,
                    'encoding': 'utf-8'
                }
            },
            
            'loggers': {
                # RabbitMQ message queue operations
                'rabbitmq.queue': {
                    'handlers': ['console', 'execution_file', 'error_file'],
                    'level': 'INFO',
                    'propagate': False
                },
                
                # Database operations
                'rabbitmq.database': {
                    'handlers': ['console', 'execution_file', 'error_file'],
                    'level': 'INFO',
                    'propagate': False
                },
                
                # API operations
                'rabbitmq.api': {
                    'handlers': ['console', 'execution_file', 'error_file'],
                    'level': 'INFO',
                    'propagate': False
                },
                
                # Agent operations
                'rabbitmq.agent': {
                    'handlers': ['console', 'agent_file', 'error_file'],
                    'level': 'INFO',
                    'propagate': False
                },
                
                # System operations
                'rabbitmq.system': {
                    'handlers': ['console', 'system_file', 'error_file'],
                    'level': 'INFO',
                    'propagate': False
                },
                
                # Audit operations
                'rabbitmq.audit': {
                    'handlers': ['audit_file'],
                    'level': 'INFO',
                    'propagate': False
                },
                
                # Root logger
                '': {
                    'handlers': ['console', 'system_file'],
                    'level': 'INFO',
                    'propagate': False
                }
            }
        }
    
    @staticmethod
    def _enhance_for_development(config: Dict[str, Any]) -> Dict[str, Any]:
        """Development-specific enhancements"""
        # Add debug handler for development
        config['handlers']['debug_file'] = {
            'class': 'logging.handlers.RotatingFileHandler',
            'level': 'DEBUG',
            'formatter': 'detailed',
            'filename': 'logs/debug.log',
            'maxBytes': 5242880,  # 5MB
            'backupCount': 2,
            'encoding': 'utf-8'
        }
        
        # Lower console level to DEBUG
        config['handlers']['console']['level'] = 'DEBUG'
        config['handlers']['console']['formatter'] = 'detailed'
        
        # Add debug handler to all loggers
        for logger_config in config['loggers'].values():
            if 'handlers' in logger_config:
                logger_config['handlers'].append('debug_file')
                logger_config['level'] = 'DEBUG'
        
        return config
    
    @staticmethod
    def _enhance_for_staging(config: Dict[str, Any]) -> Dict[str, Any]:
        """Staging-specific enhancements"""
        # Add JSON formatter for structured logging
        for logger_config in config['loggers'].values():
            if 'handlers' in logger_config and 'execution_file' in logger_config['handlers']:
                config['handlers']['execution_file']['formatter'] = 'json'
        
        return config
    
    @staticmethod
    def _enhance_for_production(config: Dict[str, Any]) -> Dict[str, Any]:
        """Production-specific enhancements"""
        # Use JSON formatting for all file handlers
        for handler_name, handler_config in config['handlers'].items():
            if handler_name.endswith('_file') and handler_name != 'audit_file':
                handler_config['formatter'] = 'json'
        
        # Reduce console verbosity
        config['handlers']['console']['level'] = 'WARNING'
        
        # Add email handler for critical errors
        config['handlers']['email_critical'] = {
            'class': 'logging.handlers.SMTPHandler',
            'level': 'CRITICAL',
            'formatter': 'detailed',
            'mailhost': os.getenv('SMTP_HOST', 'localhost'),
            'fromaddr': os.getenv('LOG_FROM_EMAIL', 'noreply@example.com'),
            'toaddrs': [os.getenv('LOG_TO_EMAIL', 'admin@example.com')],
            'subject': 'CRITICAL Error in RabbitMQ Practice App'
        }
        
        # Add critical email handler to error-prone loggers
        for logger_name in ['rabbitmq.queue', 'rabbitmq.database', 'rabbitmq.api']:
            config['loggers'][logger_name]['handlers'].append('email_critical')
        
        return config 