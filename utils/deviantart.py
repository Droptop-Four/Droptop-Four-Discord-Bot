import logging

import requests

_logger = logging.getLogger(__name__)


def initialize_deviantart(auth_url):
    """
    Initializes the connection with deviantart.

    Args:
        auth_url (str): The url to complete the authentication

    Returns:
        token (GumroadClient): The deviantart access token
    """

    try:
        response = requests.request("GET", auth_url)
        token = response.json()["access_token"]
    except Exception as e:
        _logger.critical(f"Connection to deviantart failed! -> {e}")
        token = None

    return token


def get_metadata(auth_url):
    """
    Gets the number of views, favourites and downloads.

    Args:
        auth_url (str): The url to complete the authentication

    Returns:
        views (int): The number of views
        favourites (int): The number of favourites
        downloads (int): The number of downloads
    """

    token = initialize_deviantart(auth_url)
    request_url = f"https://www.deviantart.com/api/v1/oauth2/deviation/metadata?access_token={token}&deviationids=F6A33AF1-4F50-2C57-BAD6-ACAE83BDA718&ext_submission=false&ext_camera=false&ext_stats=true&ext_collection=false&ext_gallery=false&with_session=false&mature_content=true"

    try:
        response = requests.request("GET", request_url)
        views = response.json()["metadata"][0]["stats"]["views"]
        favourites = response.json()["metadata"][0]["stats"]["favourites"]
        downloads = response.json()["metadata"][0]["stats"]["downloads"]
    except Exception as e:
        _logger.critical(f"Connection to deviantart failed! -> {e}")
        views, favourites, downloads = None, None, None

    return views, favourites, downloads
