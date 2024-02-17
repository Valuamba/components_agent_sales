import logging
import os
from logging.handlers import TimedRotatingFileHandler


log_directory = "logs"
os.makedirs(log_directory, exist_ok=True)

name = 'famaga'

# Logger configuration
logger = logging.getLogger(name)
logger.setLevel(logging.INFO)  # Set to DEBUG, INFO, WARNING, ERROR as needed

# Create a handler that writes log messages to a file, rotating at midnight.
handler = TimedRotatingFileHandler(
    os.path.join(log_directory, f"{name}.log"),
    when="midnight",
    interval=1,
    backupCount=30  # Keep 30 days of logs; adjust as needed
)
# Adjust the formatter to the desired log format
formatter = logging.Formatter('[%(asctime)s] [%(levelname)s] [%(request_id)s] - %(message)s - [%(extra_info)s]', "%Y-%m-%d %H:%M:%S")
handler.setFormatter(formatter)
logger.addHandler(handler)

console_handler = logging.StreamHandler()
console_formatter = logging.Formatter('[%(asctime)s] [%(levelname)s] - %(message)s', "%Y-%m-%d %H:%M:%S")
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)