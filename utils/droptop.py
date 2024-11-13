import json
import logging

import aiohttp

_logger = logging.getLogger(__name__)

base_url = "https://api.droptopfour.com/"
api_version = "v1"


async def fetch(session, url):
    """
    Fetch an url

    Args:
        session (aiohttp.ClientSession): The aiohttp session
        url (str): The url to fetch

    Returns:
        text (str): The text of the response
        status (int): The status code of the response
    """

    complete_url = base_url + api_version + url

    async with session.get(complete_url) as response:
        return response.status, await response.text() 


async def get_downloads(type, *, uuid=None):
    """
    Gets the number of downloads of Droptop Four

    Args:
        type (str): The type of the download. Can be 'droptop', 'app' or 'theme'
        uuid (str): The UUID of the app or theme

    Returns:
        status (int): The status code of the request
        data (dict): The data of the request
    """

    if type == "droptop":
        url = "/downloads"
    elif type == "app":
        url = f"/downloads/community-apps/{uuid}"
    elif type == "theme":
        url = f"/downloads/community-themes/{uuid}"
    else:
        return 404, None

    async with aiohttp.ClientSession() as session:
        status, data = await fetch(session, url)
        data = json.loads(data)
        return status, data


async def get_version():
    """
    Gets the version of Droptop Four

    Returns:
        status (int): The status code of the request
        data (dict): The data of the request
    """

    url = "/version"
    async with aiohttp.ClientSession() as session:
        status, data = await fetch(session, url)
        data = json.loads(data)
        return status, data


async def get_community_app(*, id=None, uuid=None, name=None, name_author=None):
    """
    Gets all the Community Apps of Droptop

    Args:
        id (int): The ID of the app
        uuid (str): The UUID of the app
        name (str): The name of the app
        name_author (str): The name & the author of the app

    Returns:
        status (int): The status code of the request
        data (dict): The data of the request
    """

    if id:
        url = f"/community-apps/id/{id}"
    elif uuid:
        url = f"/community-apps/uuid/{uuid}"
    elif name:
        url = f"/community-apps/name/{name}"
    elif name_author:
        url = f"/community-apps/name-author/{name_author}"
    else:
        url = "/community-apps"

    async with aiohttp.ClientSession() as session:
        status, data = await fetch(session, url)
        data = json.loads(data)

    return status, data


async def get_community_theme(*, id=None, uuid=None, name=None, name_author=None):
    """
    Gets all the Community Themes of Droptop

    Args:
        id (int): The ID of the theme
        uuid (str): The UUID of the theme
        name (str): The name of the theme
        name_author (str): The name & the author of the theme

    Returns:
        status (int): The status code of the request
        data (dict): The data of the request
    """

    if id:
        url = f"/community-themes/id/{id}"
    elif uuid:
        url = f"/community-themes/uuid/{uuid}"
    elif name:
        url = f"/community-themes/name/{name}"
    elif name_author:
        url = f"/community-themes/name-author/{name_author}"
    else:
        url = "/community-themes"

    async with aiohttp.ClientSession() as session:
        status, data = await fetch(session, url)
        data = json.loads(data)
        return status, data
