import logging
import os

from dotenv import load_dotenv
from pymongo import DESCENDING, MongoClient

from .droptop import get_community_app, get_community_theme

_logger = logging.getLogger(__name__)

load_dotenv()


global_data_repo = os.getenv("global_data_repo")
community_apps_repo = os.getenv("community_apps_repo")
community_themes_repo = os.getenv("community_themes_repo")


def initialize_mongodb(id):
    """
    Initializes the connection to the MongoDB database.

    Args:
        id (str): The id of the database

    Returns:
        bool: If the database was initialized
        client/e: If the database connection was initialized, the client; if not, the error
    """

    try:
        client = MongoClient(id)
        _logger.info("Connection to the database successfully initialized")
        return True, client

    except Exception as e:
        _logger.critical(f"Connection to the database failed! -> {e}")
        return False, e


async def db_new(
    db_client,
    type,
    *,
    authorised_members=None,
    title=None,
    author=None,
    description=None,
    changenotes=None,
    rmskin_name=None,
    image_name=None,
    version=None,
    uuid=None,
    author_link=None,
    github_repo=None,
):
    """
    Creates a new app or theme

    Args:
        db_client (MongoClient): The db client
        type (str): The type of package [app, theme]
        authorised_members (list): A list of authorised members to edit apps/themes
        title (str): The title of the package
        author (str): The author of the package
        description (str): The description of the package
        changenotes (str): The changenotes of the version
        rmskin_name (str): The name of the rmskin package
        image_name (str): The name of the image
        version (str): The version of the package
        uuid (str): The uuid of the package
        author_link (str): The link of the author
        github_repo (str): The link of the repo

    Returns:
        download_link: The download link of the app/theme
        image_link: The image link of the app/theme
        item_id: The id of the app/theme
        uuid (str): The uuid of the package
    """

    new_creation = False

    db = db_client[os.getenv("droptop_creations_cluster")]
    if type == "app":
        collection = db["Community_Apps"]
    elif type == "theme":
        collection = db["Community_Themes"]

    if type == "app":
        status, app = await get_community_app(uuid=uuid)
        if status == 200 and app["version"]:

            if not description:
                description = ""
            if not version:
                version = ""
            if not author_link:
                author_link = ""
            if not github_repo:
                github_repo = ""

            if changenotes:
                app["changelog"].append(
                    {"version": version, "changenotes": changenotes}
                )

                app["changelog"].sort(key=lambda x: x["version"], reverse=True)

                changelog = app["changelog"]
            else:
                changelog = app["changelog"]

            collection.update_one(
                {"uuid": uuid},
                {
                    "$set": {
                        "desc": description,
                        "version": version,
                        "author_link": author_link,
                        "official_link": github_repo,
                        "changelog": changelog,
                    }
                },
            )

            download_link = app["direct_download_link"]
            image_link = app["image_url"]
            item_id = app["id"]
        else:
            new_creation = True

    else:
        status, theme = await get_community_theme(uuid=uuid)
        if status == 200 and theme["version"] != version:

            if not description:
                description = ""
            if not version:
                version = ""
            if not author_link:
                author_link = ""
            if not github_repo:
                github_repo = ""

            if changenotes:
                theme["changelog"].append(
                    {"version": version, "changenotes": changenotes}
                )

                theme["changelog"].sort(key=lambda x: x["version"], reverse=True)

                changelog = theme["changelog"]
            else:
                changelog = theme["changelog"]

            collection.update_one(
                {"uuid": uuid},
                {
                    "$set": {
                        "desc": description,
                        "version": version,
                        "author_link": author_link,
                        "official_link": official_link,
                        "changelog": changelog,
                    }
                },
            )

            download_link = theme["direct_download_link"]
            image_link = theme["image_url"]
            item_id = theme["id"]
        else:
            new_creation = True

    if new_creation:
        last_element = collection.find_one(sort=[("id", DESCENDING)])
        item_id = last_element["id"] + 1

        if type == "app":
            download_link = f"https://github.com/Droptop-Four/{community_apps_repo}/raw/main/Apps/{rmskin_name.replace(' ', '%20')}"
            image_link = f"https://raw.githubusercontent.com/Droptop-Four/{global_data_repo}/main/data/community_apps/img/{image_name}.webp"
        else:
            download_link = f"https://github.com/Droptop-Four/{community_themes_repo}/raw/main/Themes/{rmskin_name.replace(' ', '%20')}"
            image_link = f"https://raw.githubusercontent.com/Droptop-Four/{global_data_repo}/main/data/community_themes/img/{image_name}.webp"

        if not description:
            description = ""
        if not version:
            version = ""
        if not author_link:
            author_link = ""
        if not github_repo:
            github_repo = ""

        creation = {
            "id": item_id,
            "uuid": uuid,
            "name": title,
            "author": author,
            "author_id": authorised_members[-1],
            "author_link": author_link,
            "desc": description,
            "version": version,
            "downloads": 0,
            "official_link": github_repo,
            "direct_download_link": download_link,
            "secondary_link": "",
            "image_url": image_link,
            "authorised_members": authorised_members,
            "hidden": 0,
            "changelog": [],
        }

        if changenotes:
            creation["changelog"].append(
                {"version": version, "changenotes": changenotes}
            )

            creation["changelog"].sort(key=lambda x: x["version"], reverse=True)
        else:
            creation["changelog"] = []

        collection.insert_one(creation)

    return download_link, image_link, item_id, uuid


async def db_edit(
    db_client,
    type,
    uuid,
    *,
    author=None,
    description=None,
    author_link=None,
    github_repo=None,
    authorised_members=None,
    version=None,
    changenotes=None
):
    """
    Edits the specified app or theme

    Args:
        db_client (MongoClient): The db client
        type (str): The type of package [app, theme]
        uuid (str): The uuid of the app/theme
        author (str): The author of the package
        description (str): The description of the package
        author_link (str): The link of the author
        github_repo (str): The link of the repo
        authorised_members (list): A list of authorised members to edit apps/themes
        version (str): The version of the package
        changenotes (str): The changenotes of the version

    Returns:
        download_link: The download link of the app/theme
        image_link: The image link of the app/theme
        item_id: The id of the app/theme
    """

    db = db_client[os.getenv("droptop_creations_cluster")]
    if type == "app":
        collection = db["Community_Apps"]
    elif type == "theme":
        collection = db["Community_Themes"]

    updated_data = {}

    if author:
        updated_data["author"] = author
    if description:
        updated_data["desc"] = description
    if author_link:
        updated_data["author_link"] = author_link
    if github_repo:
        updated_data["official_link"] = github_repo
    if not authorised_members:
        authorised_members = []
    
    if changenotes:
        changelog = [{"version": version, "changenotes": changenotes}]
    else:
        changelog = []

    result = collection.update_one(
        {"uuid": uuid},
        {
            "$set": updated_data,
            "$addToSet": {"authorised_members": {"$each": authorised_members}},
            "$push": {
                "changelog": {
                    "$each": [changelog],
                    "$position": 0
                }
            }
        },
    )

    if type == "app":
        _, creation = await get_community_app(uuid=uuid)
    else:
        _, creation = await get_community_theme(uuid=uuid)

    return (
        creation["direct_download_link"],
        creation["image_url"],
        creation["id"],
    )


def db_delete(db_client, type, uuid):
    """
    Deletes the specified app or theme from its json file

    Args:
        db_client (MongoClient): The db client
        type (str): The type of package [app, theme]
        uuid (str): The uuid of the app/theme
    """

    db = db_client[os.getenv("droptop_creations_cluster")]
    if type == "app":
        collection = db["Community_Apps"]
    elif type == "theme":
        collection = db["Community_Themes"]

    collection.delete_one({"uuid": uuid})
