import logging

from crowdin_api import CrowdinClient

_logger = logging.getLogger(__name__)


def initialize_crowdin(token):
    """
    Initliazes the connection with crowdin

    Args:
        token (str): The authentication token

    Returns:
        client (CrowdinClient): The crowdin client
    """

    try:
        client = CrowdinClient(token=token)
    except Exception as e:
        _logger.critical(f"Connection to crowdin failed! -> {e}")
        client = None

    return client
