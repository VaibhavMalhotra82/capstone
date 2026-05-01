from langchain_core.callbacks import BaseCallbackHandler

from backend.log import logger


class StreamlitAgentStatusCallback(BaseCallbackHandler):
    """Stream safe agent progress into Streamlit containers."""

    run_inline = True

    def __init__(self, status_container, answer_placeholder):
        super().__init__()
        self.run_inline = True
        self.status_container = status_container
        self.answer_placeholder = answer_placeholder
        self._active_tool = None
        self.had_error = False

    def _tool_label(self, tool_name):
        labels = {
            "advisory_engine": "Searching the banking knowledge base",
            "calculate_emi": "Calculating EMI",
            "calculate_sip": "Calculating SIP",
        }
        return labels.get(tool_name or "", "Using a banking assistant tool")

    def _write_status(self, message):
        try:
            self.status_container.write(message)
        except Exception as error:
            # Streamlit callbacks should never break the agent run, but logging
            # failures makes callback/context issues visible during debugging.
            logger.log_warning(f"Streamlit status write failed: {error}")

    def _update_status(self, label=None, state=None, expanded=None):
        try:
            kwargs = {}
            if label is not None:
                kwargs["label"] = label
            if state is not None:
                kwargs["state"] = state
            if expanded is not None:
                kwargs["expanded"] = expanded
            self.status_container.update(**kwargs)
        except Exception as error:
            logger.log_warning(f"Streamlit status update failed: {error}")

    def _progress(self, label, detail=None):
        logger.log_info(f"Streamlit status progress: {label}")
        self._update_status(label=label, state="running", expanded=True)
        self._write_status(detail or label)

    def _show_answer(self, text):
        if not text:
            return
        try:
            self.answer_placeholder.info(text)
        except Exception as error:
            logger.log_warning(f"Streamlit answer update failed: {error}")

    def on_agent_action(self, action, **kwargs):
        tool_name = getattr(action, "tool", None)
        self._active_tool = tool_name
        label = f"{self._tool_label(tool_name)}..."
        self._progress(label)

    def on_tool_start(self, serialized, input_str, **kwargs):
        tool_name = serialized.get("name") if isinstance(serialized, dict) else self._active_tool
        self._active_tool = tool_name
        label = f"{self._tool_label(tool_name)}..."
        self._progress(label, detail=f"{self._tool_label(tool_name)} started.")

    def on_tool_end(self, output, **kwargs):
        label = f"{self._tool_label(self._active_tool)} completed."
        self._progress(label)

    def on_agent_finish(self, finish, **kwargs):
        response_text = ""
        if getattr(finish, "return_values", None):
            response_text = finish.return_values.get("output", "")

        self._show_answer(response_text)
        self._update_status(label="Response ready.", state="complete", expanded=False)

    def on_chain_error(self, error, **kwargs):
        self.had_error = True
        self._update_status(label="An error occurred while processing the query.", state="error", expanded=True)

    def on_tool_error(self, error, **kwargs):
        self.had_error = True
        self._write_status("A tool failed while processing the query.")
        self._update_status(label="A tool failed while processing the query.", state="error", expanded=True)

    def on_llm_error(self, error, **kwargs):
        self.had_error = True
        self._update_status(label="The model call failed while preparing the response.", state="error", expanded=True)
