import logging
import time
from langchain_core.callbacks import BaseCallbackHandler

class Logger:
    """A simple logger class that wraps Python's built-in logging module."""

    def __init__(self, log_file='app.log', encoding='utf-8'):
        logging.basicConfig(filename=log_file, level=logging.INFO, format='%(asctime)s UTC - %(levelname)s - %(message)s', encoding=encoding)
        logging.Formatter.converter = time.gmtime

    def log_info(self, message):
        logging.info(message)
    
    def log_error(self, error_message):
        logging.error(f"Error: {error_message}")

    def log_warning(self, warning_message):
        logging.warning(f"Warning: {warning_message}")

logger = Logger(log_file="app.log")

class LoggingCallbackHandler(BaseCallbackHandler):
    """A LangChain callback handler that redirects agent events to Python logging."""
    
    def on_agent_action(self, action, **kwargs):
        """Logs the agent's decision to use a specific tool."""
        logger.log_info(f"Agent Action: Using tool '{action.tool}' with input '{action.tool_input}'")

    def on_tool_start(self, serialized, input_str, **kwargs):
        """Logs when a tool actually starts executing."""
        logger.log_info(f"Tool Start: {serialized.get('name')} with input: {input_str}")

    def on_tool_end(self, output, **kwargs):
        """Logs the raw output returned by the tool (Qdrant, Calculator, etc.)."""
        logger.log_info(f"Tool Result: {output}")

    def on_agent_finish(self, finish, **kwargs):
        """Logs the final response before it is sent to the user."""
        logger.log_info(f"Agent Final Answer: {finish.return_values.get('output')}")

    def on_error(self, error, **kwargs):
        """Logs any internal chain or tool errors."""
        logger.log_error(f"Agent Error: {error}")