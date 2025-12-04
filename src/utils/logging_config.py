"""Production logging configuration with structured JSON output."""

import logging
import json
import sys
import os
from datetime import datetime
from typing import Any, Callable, Dict, Optional
from functools import wraps
from contextvars import ContextVar

# Context variable for request ID
request_id_ctx: ContextVar[Optional[str]] = ContextVar('request_id', default=None)

class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging."""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_entry: Dict[str, Any] = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
            'process': record.process,
            'thread': record.thread
        }
        
        # Add request ID from context variable or record attribute
        request_id = request_id_ctx.get()
        if request_id:
            log_entry['request_id'] = request_id
        elif hasattr(record, 'request_id'):
            log_entry['request_id'] = record.request_id
        
        # Add exception info if present
        if record.exc_info:
            log_entry['exception'] = {
                'type': record.exc_info[0].__name__ if record.exc_info[0] else None,
                'message': str(record.exc_info[1]) if record.exc_info[1] else None,
                'traceback': self.formatException(record.exc_info)
            }
        
        # Add stack info if present
        if record.stack_info:
            log_entry['stack_info'] = record.stack_info
        
        # Add extra fields if present
        if hasattr(record, 'extra_fields'):
            log_entry.update(record.extra_fields)
        
        return json.dumps(log_entry, ensure_ascii=False, default=str)

def setup_production_logging(log_level: str = "INFO") -> None:
    """Set up production-ready structured logging.
    
    Note: In serverless environments (Vercel, AWS Lambda), file logging is disabled
    as the filesystem is read-only or ephemeral. Use platform logging instead.
    """
    
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
    
    # File handler for persistent logs (only in non-serverless environments)
    # Vercel and other serverless platforms have read-only or ephemeral filesystems
    is_serverless = any([
        os.getenv('VERCEL') == '1',
        os.getenv('AWS_LAMBDA_FUNCTION_NAME'),
        os.getenv('FUNCTIONS_WORKER_RUNTIME'),  # Azure Functions
        os.getenv('K_SERVICE'),  # Google Cloud Run
    ])
    
    if not is_serverless:
        try:
            file_handler = logging.FileHandler('aliexpress_api.log')
            file_handler.setFormatter(json_formatter)
            root_logger.addHandler(file_handler)
        except (OSError, PermissionError) as e:
            # Filesystem might be read-only - log to console only
            console_handler.setLevel(logging.WARNING)
            root_logger.warning(f"Could not create file handler: {e}. Using console logging only.")
    
    # Configure specific loggers
    logging.getLogger('uvicorn.access').setLevel(logging.WARNING)
    logging.getLogger('uvicorn.error').setLevel(logging.INFO)

def get_logger_with_context(name: str) -> logging.Logger:
    """Get logger with context support."""
    logger: logging.Logger = logging.getLogger(name)
    
    def log_with_context(level: int, message: str, **context: Any) -> None:
        """Log message with additional context."""
        extra: Dict[str, Dict[str, Any]] = {'extra_fields': context} if context else {}
        logger.log(level, message, extra=extra)
    
    # Add context methods
    logger.info_ctx = lambda msg, **ctx: log_with_context(logging.INFO, msg, **ctx)  # type: ignore
    logger.error_ctx = lambda msg, **ctx: log_with_context(logging.ERROR, msg, **ctx)  # type: ignore
    logger.warning_ctx = lambda msg, **ctx: log_with_context(logging.WARNING, msg, **ctx)  # type: ignore
    logger.debug_ctx = lambda msg, **ctx: log_with_context(logging.DEBUG, msg, **ctx)  # type: ignore
    
    return logger

def log_info(logger: logging.Logger, message: str, **context: Any) -> None:
    """Log INFO level message with structured context."""
    logger.info(message, extra={'extra_fields': context} if context else {})

def log_warning(logger: logging.Logger, message: str, **context: Any) -> None:
    """Log WARNING level message with structured context."""
    logger.warning(message, extra={'extra_fields': context} if context else {})

def log_error(logger: logging.Logger, message: str, exc_info: bool = False, **context: Any) -> None:
    """Log ERROR level message with structured context."""
    logger.error(message, extra={'extra_fields': context} if context else {}, exc_info=exc_info)

def log_debug(logger: logging.Logger, message: str, **context: Any) -> None:
    """Log DEBUG level message with structured context."""
    logger.debug(message, extra={'extra_fields': context} if context else {})

# Performance tracking decorator
def log_performance(operation: str) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Decorator to log operation performance."""
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            logger: logging.Logger = get_logger_with_context(func.__module__)
            start_time: datetime = datetime.utcnow()
            
            try:
                result: Any = func(*args, **kwargs)
                duration: float = (datetime.utcnow() - start_time).total_seconds()
                
                logger.info_ctx(  # type: ignore
                    f"Operation completed: {operation}",
                    operation=operation,
                    duration_seconds=duration,
                    status="success"
                )
                
                return result
            except Exception as e:
                duration: float = (datetime.utcnow() - start_time).total_seconds()
                
                logger.error_ctx(  # type: ignore
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