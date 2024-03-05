import json

import aiohttp


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

    async with session.get(url) as response:
        return await response.text(), response.status


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
        url = "https://api.droptopfour.com/v1/downloads"
    elif type == "app":
        url = f"https://api.droptopfour.com/v1/downloads/community-apps/{uuid}"
    elif type == "theme":
        url = f"https://api.droptopfour.com/v1/downloads/community-themes/{uuid}"
    else:
        return 404, None

    async with aiohttp.ClientSession() as session:
        data, status = await fetch(session, url)
        data = json.loads(data)
        return status, data


async def get_version():
    """
    Gets the version of Droptop Four
    
    Returns:
        status (int): The status code of the request
        data (dict): The data of the request
    """

    url = "https://api.droptopfour.com/v1/version"
    async with aiohttp.ClientSession() as session:
        data, status = await fetch(session, url)
        data = json.loads(data)
        return status, data


async def get_community_app(*, id=None, uuid=None, name=None):
    """
    Gets all the Community Apps of Droptop
    
    Args:
        id (int): The ID of the app
        uuid (str): The UUID of the app
        name (str): The name of the app

    Returns:
        status (int): The status code of the request
        data (dict): The data of the request
    """

    if id:
        url = f"https://api.droptopfour.com/v1/community-apps/id/{id}"
    elif name:
        url = f"https://api.droptopfour.com/v1/community-apps/name/{name}"
    elif uuid:
        url = f"https://api.droptopfour.com/v1/community-apps/uuid/{uuid}"
    else:
        url = "https://api.droptopfour.com/v1/community-apps"

    async with aiohttp.ClientSession() as session:
        data, status = await fetch(session, url)
        data = json.loads(data)
        return status, data


async def get_community_theme(*, id=None, uuid=None, name=None):
    """
    Gets all the Community Themes of Droptop
    
    Args:
        id (int): The ID of the theme
        uuid (str): The UUID of the theme
        name (str): The name of the theme

    Returns:
        status (int): The status code of the request
        data (dict): The data of the request
    """

    if id:
        url = f"https://api.droptopfour.com/v1/community-themes/id/{id}"
    elif name:
        url = f"https://api.droptopfour.com/v1/community-themes/name/{name}"
    elif uuid:
        url = f"https://api.droptopfour.com/v1/community-themes/uuid/{uuid}"
    else:
        url = "https://api.droptopfour.com/v1/community-themes"

    async with aiohttp.ClientSession() as session:
        data, status = await fetch(session, url)
        data = json.loads(data)
        return status, data
