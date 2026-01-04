"""
Structured Logging Configuration for GVD Engine
================================================
Replaces unstructured print() statements with a centralized logging system.
Supports JSON output for production and colored console output for development.

Features:
- Correlation IDs for request tracing
- Automatic context binding (run_id, user_id)
- JSON format for log aggregation systems
- Console format for development
"""
import logging
import sys
import os
from typing import Optional
from functools import wraps
import time
import uuid

# ======================================
# CONFIGURATION
# ======================================
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
LOG_FORMAT = os.getenv("LOG_FORMAT", "console")  # "json" or "console"
LOG_FILE = os.getenv("LOG_FILE", None)  # Optional file path


# ======================================
# STRUCTURED LOGGER SETUP
# ======================================
def setup_logging(
    level: str = LOG_LEVEL,
    output_format: str = LOG_FORMAT,
    log_file: Optional[str] = LOG_FILE
):
    """
    Configure structured logging for the entire application.
    
    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR)
        output_format: "json" for production, "console" for development
        log_file: Optional path to write logs to file
    
    Call this once at application startup.
    """
    # Try to use structlog if available, fallback to standard logging
    try:
        import structlog
        _setup_structlog(level, output_format, log_file)
        return True
    except ImportError:
        _setup_standard_logging(level, output_format, log_file)
        return False


def _setup_structlog(level: str, output_format: str, log_file: Optional[str]):
    """Configure structlog for JSON/console output."""
    import structlog
    
    # Configure processors based on format
    if output_format == "json":
        renderer = structlog.processors.JSONRenderer()
    else:
        renderer = structlog.dev.ConsoleRenderer(colors=True)
    
    processors = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        renderer,
    ]
    
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(getattr(logging, level)),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )
    
    # Also configure standard logging to use structlog
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, level),
    )
    
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(getattr(logging, level))
        logging.getLogger().addHandler(file_handler)


def _setup_standard_logging(level: str, output_format: str, log_file: Optional[str]):
    """Fallback to standard Python logging."""
    if output_format == "json":
        log_format = '{"timestamp": "%(asctime)s", "level": "%(levelname)s", "logger": "%(name)s", "message": "%(message)s"}'
    else:
        log_format = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
    
    handlers = [logging.StreamHandler(sys.stdout)]
    
    if log_file:
        handlers.append(logging.FileHandler(log_file))
    
    logging.basicConfig(
        level=getattr(logging, level),
        format=log_format,
        handlers=handlers,
        force=True
    )


# ======================================
# CONTEXT BINDING (Correlation IDs)
# ======================================
_context_vars = {}

def bind_context(**kwargs):
    """
    Bind context variables to all subsequent log messages.
    
    Example:
        bind_context(run_id="abc123", user_id="user1")
        logger.info("Processing started")  # includes run_id and user_id
    """
    global _context_vars
    _context_vars.update(kwargs)
    
    try:
        import structlog
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(**_context_vars)
    except ImportError:
        pass  # Context not supported in standard logging fallback


def clear_context():
    """Clear all bound context variables."""
    global _context_vars
    _context_vars = {}
    
    try:
        import structlog
        structlog.contextvars.clear_contextvars()
    except ImportError:
        pass


def get_run_id() -> str:
    """Generate a unique run ID for request correlation."""
    return str(uuid.uuid4())[:8]


# ======================================
# LOGGING DECORATORS
# ======================================
def log_execution(logger_name: str = "GVD"):
    """
    Decorator to log function entry, exit, and duration.
    
    Example:
        @log_execution()
        def my_function():
            ...
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            logger = logging.getLogger(logger_name)
            func_name = func.__name__
            
            start_time = time.time()
            logger.info(f"→ {func_name} started")
            
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                logger.info(f"← {func_name} completed in {duration:.2f}s")
                return result
            except Exception as e:
                duration = time.time() - start_time
                logger.error(f"✗ {func_name} failed after {duration:.2f}s: {e}")
                raise
        
        return wrapper
    return decorator


# ======================================
# CONVENIENCE GETTERS
# ======================================
def get_logger(name: str):
    """
    Get a logger instance with the given name.
    
    This is the main entry point for getting loggers throughout the codebase.
    Works with both structlog (if available) and standard logging.
    """
    try:
        import structlog
        return structlog.get_logger(name)
    except ImportError:
        return logging.getLogger(name)


# ======================================
# AUTO-CONFIGURE ON IMPORT
# ======================================
# Configure logging with defaults when module is imported
setup_logging()
