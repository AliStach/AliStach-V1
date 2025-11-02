"""Production logging configuration with structured JSON output."""

import logging
import json
import sys
from datetime import datetime
from typing import Dict, Any


class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging."""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_entry = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        # Add exception info if present
        if record.exc_info:
            log_entry['exception'] = self.formatException(record.exc_info)
        
        # Add extra fields if present
        if hasattr(record, 'extra_fields'):
            log_entry.update(record.extra_fields)
        
        return json.dumps(log_entry, ensure_ascii=False)


def setup_production_logging(log_level: str = "INFO") -> None:
    """Set up production-ready structured logging."""
    
    # Create JSON formatter
    json_formatter = JSONFormatter()
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))
    
    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Console handler with JSON formatting
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(json_formatter)
    root_logger.addHandler(console_handler)
    
    # File handler for persistent logs
    file_handler = logging.FileHandler('aliexpress_api.log')
    file_handler.setFormatter(json_formatter)
    root_logger.addHandler(file_handler)
    
    # Configure specific loggers
    logging.getLogger('uvicorn.access').setLevel(logging.WARNING)
    logging.getLogger('uvicorn.error').setLevel(logging.INFO)


def get_logger_with_context(name: str) -> logging.Logger:
    """Get logger with context support."""
    logger = logging.getLogger(name)
    
    def log_with_context(level: int, message: str, **context):
        """Log message with additional context."""
        extra = {'extra_fields': context} if context else {}
        logger.log(level, message, extra=extra)
    
    # Add context methods
    logger.info_ctx = lambda msg, **ctx: log_with_context(logging.INFO, msg, **ctx)
    logger.error_ctx = lambda msg, **ctx: log_with_context(logging.ERROR, msg, **ctx)
    logger.warning_ctx = lambda msg, **ctx: log_with_context(logging.WARNING, msg, **ctx)
    
    return logger


# Performance tracking decorator
def log_performance(operation: str):
    """Decorator to log operation performance."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            logger = get_logger_with_context(func.__module__)
            start_time = datetime.utcnow()
            
            try:
                result = func(*args, **kwargs)
                duration = (datetime.utcnow() - start_time).total_seconds()
                
                logger.info_ctx(
                    f"Operation completed: {operation}",
                    operation=operation,
                    duration_seconds=duration,
                    status="success"
                )
                
                return result
            except Exception as e:
                duration = (datetime.utcnow() - start_time).total_seconds()
                
                logger.error_ctx(
                    f"Operation failed: {operation}",
                    operation=operation,
                    duration_seconds=duration,
                    status="error",
                    error_type=type(e).__name__,
                    error_message=str(e)
                )
                
                raise
        return wrapper
    return decorator