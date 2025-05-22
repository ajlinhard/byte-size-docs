# Python Logging Cheatsheet

Here's a comprehensive guide to using Python's logging package, starting with the basics and progressing to more advanced features.

## Basic Example

```python
import logging

# Configure basic logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Create a logger
logger = logging.getLogger(__name__)

# Log messages at different levels
logger.debug("This is a debug message")
logger.info("This is an info message")
logger.warning("This is a warning message")
logger.error("This is an error message")
logger.critical("This is a critical message")
```

## Common Functions and Features

### Logging Levels
- `DEBUG` (10): Detailed information for debugging
- `INFO` (20): Confirmation that things are working as expected
- `WARNING` (30): Indication of a potential problem
- `ERROR` (40): Error that prevented a function from working
- `CRITICAL` (50): Critical error that may cause the program to terminate

### Configuration Methods
```python
# Basic configuration
logging.basicConfig(
    filename='app.log',  # Output to file
    filemode='w',        # 'w' to overwrite, 'a' to append
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Set level for specific logger
logger.setLevel(logging.DEBUG)

# Create handler and set level
handler = logging.FileHandler('app.log')
handler.setLevel(logging.ERROR)

# Create formatter and add to handler
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

# Add handler to logger
logger.addHandler(handler)
```

### Formatting Options
Common format specifiers:
- `%(asctime)s`: Human-readable date/time
- `%(name)s`: Logger name
- `%(levelname)s`: Level name (DEBUG, INFO, etc.)
- `%(levelno)d`: Level number (10, 20, etc.)
- `%(pathname)s`: Full path to the source file
- `%(filename)s`: File name
- `%(funcName)s`: Function name
- `%(lineno)d`: Line number
- `%(message)s`: The logged message
- `%(process)d`: Process ID
- `%(threadName)s`: Thread name

## Advanced Example

```python
import logging
import logging.handlers
import os

def setup_logger():
    # Create logger
    logger = logging.getLogger('advanced_app')
    logger.setLevel(logging.DEBUG)
    
    # Prevent adding handlers multiple times
    if logger.handlers:
        return logger
    
    # Create directory for logs if it doesn't exist
    os.makedirs('logs', exist_ok=True)
    
    # File handler for all logs
    file_handler = logging.handlers.RotatingFileHandler(
        'logs/app.log',
        maxBytes=10485760,  # 10MB
        backupCount=5
    )
    file_handler.setLevel(logging.DEBUG)
    
    # File handler for errors only
    error_handler = logging.handlers.RotatingFileHandler(
        'logs/error.log',
        maxBytes=10485760,
        backupCount=5
    )
    error_handler.setLevel(logging.ERROR)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'
    )
    simple_formatter = logging.Formatter('%(levelname)s: %(message)s')
    
    # Add formatters to handlers
    file_handler.setFormatter(detailed_formatter)
    error_handler.setFormatter(detailed_formatter)
    console_handler.setFormatter(simple_formatter)
    
    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(error_handler)
    logger.addHandler(console_handler)
    
    return logger

# Usage
logger = setup_logger()
logger.debug("Debug message")
logger.info("Info message")
logger.warning("Warning message")
logger.error("Error message")
logger.critical("Critical message")

# Log an exception
try:
    1/0
except Exception as e:
    logger.exception("An error occurred")  # Logs traceback automatically
```

## Advanced Features

### Custom Filters
```python
class ContextFilter(logging.Filter):
    def __init__(self, param=None):
        self.param = param
        
    def filter(self, record):
        record.custom_attribute = self.param
        return True

logger = logging.getLogger()
f = ContextFilter('custom_value')
logger.addFilter(f)
```

### LoggerAdapter for Context
```python
class CustomAdapter(logging.LoggerAdapter):
    def process(self, msg, kwargs):
        return '[%s] %s' % (self.extra['user'], msg), kwargs

logger = logging.getLogger()
adapter = CustomAdapter(logger, {'user': 'admin'})
adapter.info("This message has context")
```

### Handlers
- `StreamHandler`: Logs to streams (stdout/stderr)
- `FileHandler`: Logs to a file
- `RotatingFileHandler`: Logs to a file, rotating when size limit is reached
- `TimedRotatingFileHandler`: Logs to a file, rotating at specified time intervals
- `SocketHandler`: Logs to a network socket
- `SMTPHandler`: Sends log via email
- `SysLogHandler`: Logs to syslog
- `NullHandler`: Does nothing (useful for libraries)

### Configuration from file
```python
import logging.config

# Load from a file
logging.config.fileConfig('logging.conf')

# Or use a dictionary config
config_dict = {
    'version': 1,
    'formatters': {
        'standard': {
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'INFO',
            'formatter': 'standard',
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': 'app.log',
            'level': 'DEBUG',
            'formatter': 'standard',
        }
    },
    'loggers': {
        '': {  # Root logger
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': True
        }
    }
}
logging.config.dictConfig(config_dict)
```

### Best Practices
1. Use `__name__` for logger names to create a hierarchy
2. Set appropriate log levels for different environments
3. Use context information in logs for easier debugging
4. Configure handlers at the application level, not in libraries
5. Use `exception()` for logging exceptions to capture tracebacks
6. Use formatters consistently across handlers
7. Consider using JSON formatting for logs in production for easier parsing
