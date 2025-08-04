import logging
import config
import os

# Make sure logs directory exists
os.makedirs("logs", exist_ok=True)

# Get the root logger (or a project-wide logger)
logger = logging.getLogger("pokepy")
logger.setLevel(config.LOG_LEVEL)
logger.handlers.clear()  # prevent duplicate handlers

# File handler (overwrite each run)
file_handler = logging.FileHandler(config.LOG_FILE, mode="w")
file_handler.setLevel(config.LOG_LEVEL)

# Console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(config.LOG_LEVEL)

# Formatter
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# Attach handlers
logger.addHandler(file_handler)
logger.addHandler(console_handler)
