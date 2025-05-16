import logging
from main import app, start_bogo_sort

logging.info("WSGI entry point: Initializing application...")
start_bogo_sort()
logging.info("WSGI entry point: Application initialized successfully.")
