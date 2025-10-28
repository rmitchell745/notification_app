import logging
from logging.handlers import TimedRotatingFileHandler
import os

# Create a logs directory if it doesn't exist
log_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)),"logs")
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

# Configure the logger
logger = logging.getLogger("weather_app")
logger.setLevel(logging.INFO)  # Set the minimum logging level

# Create a file handler with timed rotation
log_file = os.path.join(log_dir, "weather_app.log")
file_handler = TimedRotatingFileHandler(
    log_file, when="W0", interval=1, backupCount=5
)
# when="W0" means rotate every Monday (W0 to W6 for Sunday to Saturday)
# interval=1 means rotate every 1 week
# backupCount=5 means keep 5 weeks of backup logs

# Create a formatter and add it to the handler
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
file_handler.setFormatter(formatter)

# Add the file handler to the logger
logger.addHandler(file_handler)

# Optionally, add a stream handler to output logs to the console
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)

logger.info("Logger configured.")
