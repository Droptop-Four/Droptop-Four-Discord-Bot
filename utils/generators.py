import logging
import uuid

_logger = logging.getLogger(__name__)


def generate_uuid_string():
    """
    Generates a uuid.

    Returns:
        string (str): The generated uuid
    """

    string = str(uuid.uuid4())
    return string
