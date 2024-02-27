from crowdin_api import CrowdinClient


def initialize_crowdin(token):
    """
    Initliazes the connection with crowdin

    Args:
            token (str): The authentication token

    Returns:
            client (CrowdinClient): The crowdin client
    """

    client = CrowdinClient(token=token)

    return client
