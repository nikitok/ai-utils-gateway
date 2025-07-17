"""
Centralized logging configuration with Rich formatting
"""
import logging
from rich.console import Console
from rich.logging import RichHandler


# Create a global console instance
console = Console()

def setup_logger(name: str = None, level: int = logging.INFO) -> logging.Logger:
    """
    Setup a logger with Rich formatting
    
    Args:
        name: Logger name (defaults to root logger if None)
        level: Logging level (defaults to INFO)
    
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    
    # Only configure if not already configured
    if not logger.handlers:
        logger.setLevel(level)
        
        # Create Rich handler with our console
        handler = RichHandler(
            console=console,
            rich_tracebacks=True,
            show_time=True,
            show_path=False,
            omit_repeated_times=False,
            log_time_format="[%m/%d/%y %H:%M:%S]"
        )
        handler.setFormatter(logging.Formatter("%(message)s"))
        
        logger.addHandler(handler)
        logger.propagate = False
    
    return logger


def get_logger(name: str = None) -> logging.Logger:
    """
    Get or create a logger with Rich formatting
    
    Args:
        name: Logger name
    
    Returns:
        Logger instance
    """
    return setup_logger(name)


# Export console for direct use when needed
__all__ = ['console', 'setup_logger', 'get_logger']