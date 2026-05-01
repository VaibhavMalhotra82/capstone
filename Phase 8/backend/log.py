import logging
import time
from langchain_core.callbacks import BaseCallbackHandler
from langchain_community.callbacks.streamlit.streamlit_callback_handler import (
    LLMThought,
    StreamlitCallbackHandler as InternalStreamlitCallbackHandler,
)
from streamlit.errors import NoSessionContext

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

class SafeStreamlitCallbackHandler(InternalStreamlitCallbackHandler):
    """A Streamlit callback handler that degrades cleanly outside a live Streamlit session."""

    _MISSING_THOUGHT_ERROR = "Current LLMThought is unexpectedly None!"

    def _require_current_thought(self):
        if self._current_thought is None:
            self._current_thought = LLMThought(
                parent_container=self._parent_container,
                expanded=self._expand_new_thoughts,
                collapse_on_complete=self._collapse_completed_thoughts,
                labeler=self._thought_labeler,
            )
        return self._current_thought

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._streamlit_context_available = True

    def _handle_streamlit_error(self, error):
        if isinstance(error, NoSessionContext):
            self._streamlit_context_available = False
            logger.log_warning("Streamlit session context is unavailable; skipping UI callback updates.")
            return True

        if isinstance(error, RuntimeError) and self._MISSING_THOUGHT_ERROR in str(error):
            self._current_thought = None
            return True

        return False

    def _run_streamlit_callback(self, method_name, *args, retry_on_missing_thought=False, **kwargs):
        if not self._streamlit_context_available:
            return None

        method = getattr(super(), method_name)
        try:
            if retry_on_missing_thought:
                self._require_current_thought()
            return method(*args, **kwargs)
        except Exception as error:
            if not self._handle_streamlit_error(error):
                raise

            if (
                retry_on_missing_thought
                and self._streamlit_context_available
                and isinstance(error, RuntimeError)
                and self._MISSING_THOUGHT_ERROR in str(error)
            ):
                try:
                    self._require_current_thought()
                    return method(*args, **kwargs)
                except Exception as retry_error:
                    if not self._handle_streamlit_error(retry_error):
                        raise

        return None

    def on_llm_start(self, serialized, prompts, **kwargs):
        return self._run_streamlit_callback("on_llm_start", serialized, prompts, **kwargs)

    def on_llm_new_token(self, token, **kwargs):
        return self._run_streamlit_callback("on_llm_new_token", token, **kwargs)

    def on_llm_end(self, response, **kwargs):
        return self._run_streamlit_callback("on_llm_end", response, **kwargs)

    def on_llm_error(self, error, **kwargs):
        return self._run_streamlit_callback("on_llm_error", error, **kwargs)

    def on_agent_action(self, action, **kwargs):
        return self._run_streamlit_callback(
            "on_agent_action",
            action,
            retry_on_missing_thought=True,
            **kwargs,
        )

    def on_tool_start(self, serialized, input_str, **kwargs):
        return self._run_streamlit_callback(
            "on_tool_start",
            serialized,
            input_str,
            retry_on_missing_thought=True,
            **kwargs,
        )

    def on_tool_end(self, output, **kwargs):
        return self._run_streamlit_callback("on_tool_end", output, **kwargs)

    def on_tool_error(self, error, **kwargs):
        return self._run_streamlit_callback("on_tool_error", error, **kwargs)

    def on_agent_finish(self, finish, **kwargs):
        return self._run_streamlit_callback("on_agent_finish", finish, **kwargs)

    def on_chain_error(self, error, **kwargs):
        return self._run_streamlit_callback("on_chain_error", error, **kwargs)


class UIAgentCallbackHandler(LoggingCallbackHandler):
    """Callback handler that also captures tool outputs for UI display."""

    def __init__(self):
        super().__init__()
        self.source_documents = []
        self.last_tool_output = None

    def on_tool_end(self, output, **kwargs):
        super().on_tool_end(output, **kwargs)
        self.last_tool_output = output

        if isinstance(output, dict):
            if output.get('source_documents'):
                self.source_documents = output['source_documents']
            elif isinstance(output.get('result'), dict) and output['result'].get('source_documents'):
                self.source_documents = output['result']['source_documents']
