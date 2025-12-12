import logging
import sys
from typing import Optional
from pathlib import Path
import os

class Logger:
    def __init__(self, name: str = "app", level: str = "INFO", log_file: Optional[str] = None):
        """
        Initialize a logger with specified level and optional file output.
        
        Args:
            name: Logger name (typically __name__ from the calling module)
            level: Logging level (DEBUG, INFO, WARNING, ERROR, FATAL)
            log_file: Optional file path to write logs to
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, level.upper(), logging.INFO))
        
        # Prevent adding multiple handlers if logger already exists
        if self.logger.handlers:
            return
            
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Create console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.DEBUG)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
        
        # Create file handler if specified
        if log_file:
            # Ensure directory exists
            log_path = Path(log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)
            
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)
    
    def debug(self, message: str):
        """Log a debug message."""
        self.logger.debug(message)
    
    def info(self, message: str):
        """Log an info message."""
        self.logger.info(message)
    
    def warning(self, message: str):
        """Log a warning message."""
        self.logger.warning(message)
    
    def error(self, message: str):
        """Log an error message."""
        self.logger.error(message)
    
    def fatal(self, message: str):
        """Log a fatal/critical message."""
        self.logger.critical(message)
    
    def exception(self, message: str):
        """Log an exception with traceback."""
        self.logger.exception(message)