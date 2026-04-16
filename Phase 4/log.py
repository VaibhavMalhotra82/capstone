import logging
import time

class Logger:
    def __init__(self, log_file='app.log'):
        logging.basicConfig(filename=log_file, level=logging.INFO, format='%(asctime)s UTC - %(levelname)s - %(message)s')
        logging.Formatter.converter = time.gmtime

    def log_info(self, message):
        logging.info(message)
    
    def log_error(self, error_message):
        logging.error(f"Error: {error_message}")

    def log_warning(self, warning_message):
        logging.warning(f"Warning: {warning_message}")