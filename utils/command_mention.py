import logging

_logger = logging.getLogger(__name__)


def command_mention(name, id):
    """
    Mentions a slash command.

    Args:
        name (str): The name of the command
        id (str): The id of the command

    Returns:
        mention (str): The mention of the command
    """

    mention = f"</{name}:{id}>"
    return mention
