import json
import os
from backend.log import logger
from langchain_core.messages import HumanMessage, messages_to_dict, messages_from_dict


def store_feedback(session_id: str, feedback: list):
    """Saves user feedback to a feedback file."""
    try:
        feedback_path = f"feedback_{session_id}.json"
        feedback_messages = [
            item if hasattr(item, "type") else HumanMessage(content=str(item))
            for item in feedback
        ]
        dict_feedback = {"feedback": messages_to_dict(feedback_messages)}
        with open(feedback_path, "w") as f:
            json.dump(dict_feedback, f)

        logger.log_info(f"Feedback stored for session {session_id}")
        return "success"
    except Exception as e:
        logger.log_error(f"Error storing feedback for session {session_id}: {e}")
        return "failure"


def load_feedback(session_id: str) -> list:
    """Loads user feedback from a feedback file, if it exists."""
    feedback_path = f"feedback_{session_id}.json"
    if os.path.exists(feedback_path):
        with open(feedback_path, "r") as f:
            data = json.load(f)
            logger.log_info(f"Feedback loaded for session {session_id}")
            return messages_from_dict(data["feedback"])
    else:
        logger.log_info(f"No feedback found for session {session_id}")
        return []
