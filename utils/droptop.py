import aiohttp
import json

async def fetch(session, url):
    """Fetch an url"""

    async with session.get(url) as response:
        return await response.text()


async def get_downloads():
    """Gets the number of downloads of Droptop Four"""

    url = "https://api.droptopfour.com/v1/downloads"
    async with aiohttp.ClientSession() as session:
        data = await fetch(session, url)
        data = json.loads(data)
        return data["basic_downloads"], data["update_downloads"]

