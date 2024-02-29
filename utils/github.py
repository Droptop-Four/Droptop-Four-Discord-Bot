import base64
import json
import os
from pathlib import Path

import github
import requests
from dotenv import load_dotenv

from .generators import generate_uuid_string
from .time_utils import version_date

load_dotenv()

auth_app = os.getenv("github_auth_app")

global_data_repo = os.getenv("global_data_repo")
community_apps_repo = os.getenv("community_apps_repo")
community_themes_repo = os.getenv("community_themes_repo")


def initialize_github(private_key):
    """
    Initializes the connection with github.

    Args:
            private_key (str): The private key

    Returns:
            g (Github): The github instance
            all_files (list): Empty list
    """

    auth = github.Auth.AppAuth(auth_app, private_key)
    gi = github.GithubIntegration(auth=auth)
    installation = gi.get_installations()[0]
    g = installation.get_github_for_installation()

    all_files = []
    return g, all_files


def github_reader(private_key, path):
    """
    Reads a file from github and returns it as a json object.

    Args:
            private_key (str): The authentication private_key
            path (str): Path to file on github

    Returns:
            data: (json): JSON object of file contents
    """

    g, all_files = initialize_github(private_key)
    repo = g.get_repo("Droptop-Four/GlobalData")

    contents = repo.get_contents(path)
    encoding = contents.encoding
    if encoding == "base64":
        file_content = base64.b64decode(contents.content).decode()
    data = json.loads(file_content)
    return data


def get_releases_downloads(private_key):
    """
    Gets the number of downloads across all releases.

    Args:
            private_key (str): The authentication private_key

    Returns:
            basic_downloads (int): The number of downloads of the Basic variant
            update_downloads (int): The number of downloads of the Update variant
    """

    g, all_files = initialize_github(private_key)
    repo = g.get_repo("Droptop-Four/Droptop-Four")
    basic_downloads = 0
    update_downloads = 0
    releases = repo.get_releases()
    for release in releases:
        assets = release.get_assets()

        basic_downloads += assets[0].download_count
        update_downloads += assets[1].download_count

    return basic_downloads, update_downloads


def get_stars(private_key):
    """
    Gets the number of stars across all repos.

    Args:
            private_key (str): The authentication private_key

    Returns:
            stars (int): The number of stars
    """

    g, all_files = initialize_github(private_key)
    org = g.get_organization("Droptop-Four")
    repos = org.get_repos()
    stars = 0
    for repo in repos:
        stars += repo.stargazers_count

    return stars


def edit_release(private_key, version, cl_features, cl_modifications, cl_bugfixes):
    """
    Edits the specific release on Github

    Args:
            private_key (str): The authentication private_key
            version (str): The version of the package
            cl_features (list): A list of features of a droptop new version
            cl_modifications (list): A list of modifications of a droptop new version
            cl_bugfixes (list): A list of bug fixes of a droptop new version

    Returns:
            edited (bool): If the release was edited
    """

    g, all_files = initialize_github(private_key)
    repo = g.get_repo("Droptop-Four/Droptop-Four")

    mainversion, miniversion = version

    try:
        release = repo.get_release(f"v{mainversion}.{miniversion}")
        message = ""

        if (len(cl_features) >= 1) and (cl_features[0] != ""):
            message += "## New features 🆕\n"
            for feature in cl_features:
                message += f"- {feature}\n"

        if (len(cl_modifications) >= 1) and (cl_modifications[0] != ""):
            message += "## Modifications ⚠️\n"
            for modification in cl_modifications:
                message += f"- {modification}\n"

        if (len(cl_bugfixes) >= 1) and (cl_bugfixes[0] != ""):
            message += "## Bug fixes 🪲\n"
            for bugfix in cl_bugfixes:
                message += f"- {bugfix}\n"

        message += f"\n\n# >>> :arrow_down: [Download Droptop](https://github.com/Droptop-Four/Droptop-Four/releases/download/v{mainversion}.{miniversion}/Droptop_Basic_Version.rmskin) :arrow_down: <<<\n"

        release.update_release(
            name=f"Droptop Four v{mainversion}.{miniversion}", message=message
        )
        edited = True

    except:
        edited = False

    return edited


def get_followers(private_key):
    """
    Gets the number of followers of the organization.

    Args:
            private_key (str): The authentication private_key

    Returns:
            followers (int): The number of followers
    """

    g, all_files = initialize_github(private_key)
    org = g.get_organization("Droptop-Four")
    followers = org.followers

    return followers


def push_rmskin(private_key, type, package_name):
    """
    Pushes the rmskin package to github.

    Args:
            private_key (str): The authentication private_key
            type (str): The type of package [app, theme]
            package_name (str): The name of the package

    Returns:
            creation (bool): if the package was created (True) or it was already present and was only updated (False)
    """

    g, all_files = initialize_github(private_key)
    if type == "app":
        repo = g.get_repo(f"Droptop-Four/{community_apps_repo}")
        git_prefix = "Apps/"
    else:
        repo = g.get_repo(f"Droptop-Four/{community_themes_repo}")
        git_prefix = "Themes/"

    contents = repo.get_contents("")

    while contents:
        file_content = contents.pop(0)
        if file_content.type == "dir":
            contents.extend(repo.get_contents(file_content.path))
        else:
            file = file_content
            all_files.append(
                str(file).replace('ContentFile(path="', "").replace('")', "")
            )

    with open(f"tmp/{package_name}", "rb") as file:
        content = file.read()

    git_file = git_prefix + package_name

    if git_file in all_files:
        contents = repo.get_contents(git_file)
        if type == "app":
            repo.update_file(
                contents.path, f"{version_date()}", content, contents.sha, branch="main"
            )
        else:
            repo.update_file(
                contents.path, f"{version_date()}", content, contents.sha, branch="main"
            )
        creation = False
        return creation

    else:
        if type == "app":
            repo.create_file(git_file, f"{version_date()}", content, branch="main")
        else:
            repo.create_file(git_file, f"{version_date()}", content, branch="main")
        creation = True
        return creation


def push_image(private_key, type, image_name):
    """
    Pushes the image to github

    Args:
            private_key (str): The authentication private_key
            type (str): The type of package [app, theme]
            image_name (str): The name of the image

    Returns:
            creation (bool): if the image was created (True) or it was already present and was only updated (False)
    """

    g, all_files = initialize_github(private_key)
    repo = g.get_repo(f"Droptop-Four/{global_data_repo}")

    if type == "app":
        git_prefix = "data/community_apps/img/"
    else:
        git_prefix = "data/community_themes/img/"

    contents = repo.get_contents("")

    while contents:
        file_content = contents.pop(0)
        if file_content.type == "dir":
            contents.extend(repo.get_contents(file_content.path))
        else:
            file = file_content
            all_files.append(
                str(file).replace('ContentFile(path="', "").replace('")', "")
            )

    with open(f"tmp/{image_name}.webp", "rb") as file:
        content = file.read()

    git_file = git_prefix + image_name + ".webp"

    if git_file in all_files:
        contents = repo.get_contents(git_file)
        if type == "app":
            repo.update_file(
                contents.path, f"{version_date()}", content, contents.sha, branch="main"
            )
        else:
            repo.update_file(
                contents.path, f"{version_date()}", content, contents.sha, branch="main"
            )
        creation = False
        return creation

    else:
        if type == "app":
            repo.create_file(git_file, f"{version_date()}", content, branch="main")
        else:
            repo.create_file(git_file, f"{version_date()}", content, branch="main")
        creation = True
        return creation


def json_update(
    private_key,
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
    ann_date=None,
    ann_expiration=None,
    announcement=None,
    ann_type=None,
    ann_scope=None,
    cl_features=None,
    cl_modifications=None,
    cl_bugfixes=None,
):
    """
    Updates the json file with the new package information

    Args:
            private_key (str): The authentication private_key
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
            ann_date (float): The date of the announcement
            ann_expiration (float): The expiration date of the announcement
            announcement (str): The announcement
            ann_type (str): The type of announcement [Important, Warning, Info]
            ann_scope (str): The scope of the announcement [App, Website, Website & App]
            cl_features (list): A list of features of a droptop new version
            cl_modifications (list): A list of modifications of a droptop new version
            cl_bugfixes (list): A list of bug fixes of a droptop new version

    Returns:
            creation (bool): if the app inside of the json was created (True) or it was already present and was only updated (False)
    """

    g, all_files = initialize_github(private_key)

    repo = g.get_repo(f"Droptop-Four/{global_data_repo}")

    if type == "app":
        content = repo.get_contents("data/community_apps/community_apps.json")
        community_json = github_reader(
            private_key, "data/community_apps/community_apps.json"
        )
    elif type == "theme":
        content = repo.get_contents("data/community_themes/community_themes.json")
        community_json = github_reader(
            private_key, "data/community_themes/community_themes.json"
        )
    elif type == "announcement":
        content = repo.get_contents("data/announcements.json")
        announcements_json = github_reader(private_key, "data/announcements.json")
    elif type == "changelog":
        content = repo.get_contents("data/changelog.json")
        changelog_json = github_reader(private_key, "data/changelog.json")
    else:
        content = repo.get_contents("data/version.json")

    itemlist = []
    idlist = []
    new_item = False

    if type == "app":
        for item in community_json["apps"]:
            app_tags = item["app"]
            itemlist.append(app_tags["name"])
            idlist.append(app_tags["id"])
            if app_tags["uuid"] == uuid and version != app_tags["version"]:

                if not description:
                    description = ""
                if not version:
                    version = ""
                if not author_link:
                    author_link = ""
                if not github_repo:
                    github_repo = ""

                app_tags["desc"] = description
                app_tags["version"] = version
                app_tags["author_link"] = author_link
                app_tags["official_link"] = github_repo

                if changenotes:
                    app_tags["changelog"].append(
                        {"version": version, "changenotes": changenotes}
                    )

                    app_tags["changelog"].sort(key=lambda x: x["version"], reverse=True)

                json.dumps(community_json, indent=4)
                temp_json = Path("tmp/community_apps.json")
                with open(temp_json, "w+", encoding="utf-8") as f:
                    json.dump(community_json, f, ensure_ascii=False, indent=4)
                    f.seek(0)
                    json_content = f.read()
                repo.update_file(
                    content.path,
                    f"{version_date()}",
                    json_content,
                    content.sha,
                    branch="main",
                )
                download_link = app_tags["direct_download_link"]
                image_link = app_tags["image_url"]
                item_id = app_tags["id"]
                # uuid = app_tags["uuid"]
                temp_json.unlink()
            elif app_tags["uuid"] == uuid and version == app_tags["version"]:

                if not description:
                    description = ""
                if not version:
                    version = ""
                if not author_link:
                    author_link = ""
                if not github_repo:
                    github_repo = ""

                app_tags["desc"] = description
                app_tags["version"] = version
                app_tags["author_link"] = author_link
                app_tags["official_link"] = github_repo

                if changenotes:
                    app_tags["changelog"].append(
                        {"version": version, "changenotes": changenotes}
                    )

                    app_tags["changelog"].sort(key=lambda x: x["version"], reverse=True)

                json.dumps(community_json, indent=4)
                temp_json = Path("tmp/community_apps.json")
                with open(temp_json, "w+", encoding="utf-8") as f:
                    json.dump(community_json, f, ensure_ascii=False, indent=4)
                    f.seek(0)
                    json_content = f.read()
                repo.update_file(
                    content.path,
                    f"{version_date()}",
                    json_content,
                    content.sha,
                    branch="main",
                )
                download_link = app_tags["direct_download_link"]
                image_link = app_tags["image_url"]
                item_id = app_tags["id"]
                # uuid = app_tags["uuid"]
                temp_json.unlink()
            else:
                pass

    elif type == "theme":

        for item in community_json["themes"]:
            theme_tags = item["theme"]
            itemlist.append(theme_tags["name"])
            idlist.append(theme_tags["id"])

            if theme_tags["name"] == title:

                if not description:
                    description = ""
                if not version:
                    version = ""
                if not author_link:
                    author_link = ""
                if not github_repo:
                    github_repo = ""

                theme_tags["desc"] = description
                theme_tags["version"] = version
                theme_tags["author_link"] = author_link
                theme_tags["official_link"] = github_repo

                if changenotes:
                    theme_tags["changelog"].append(
                        {"version": version, "changenotes": changenotes}
                    )

                    theme_tags["changelog"].sort(
                        key=lambda x: x["version"], reverse=True
                    )

                json.dumps(community_json, indent=4)
                temp_json = Path("tmp/community_themes.json")
                with open(temp_json, "w+", encoding="utf-8") as f:
                    json.dump(community_json, f, ensure_ascii=False, indent=4)
                    f.seek(0)
                    json_content = f.read()
                repo.update_file(
                    content.path,
                    f"{version_date()}",
                    json_content,
                    content.sha,
                    branch="main",
                )
                download_link = theme_tags["direct_download_link"]
                image_link = theme_tags["image_url"]
                item_id = theme_tags["id"]
                uuid = theme_tags["uuid"]
                temp_json.unlink()
            else:
                pass

    elif type == "announcement":

        if ann_date is not None:
            ann_date = float(ann_date)
        if ann_expiration is not None:
            ann_expiration = float(ann_expiration)

        if ann_scope == "Website":
            if not ann_expiration:
                announcements_json["website"] = {
                    "date": ann_date,
                    "expiration": ann_expiration,
                    "announcement": f"{announcement}",
                    "type": f"{ann_type}",
                }
            else:
                announcements_json["website"] = {
                    "date": ann_date,
                    "expiration": ann_expiration,
                    "announcement": f"{announcement}",
                    "type": f"{ann_type}",
                }
        elif ann_scope == "App":
            if not ann_expiration:
                announcements_json["app"] = {
                    "date": ann_date,
                    "expiration": ann_expiration,
                    "announcement": f"{announcement}",
                    "type": f"{ann_type}",
                }
            else:
                announcements_json["app"] = {
                    "date": ann_date,
                    "expiration": ann_expiration,
                    "announcement": f"{announcement}",
                    "type": f"{ann_type}",
                }
        else:
            if not ann_expiration:
                announcements_json = {
                    "app": {
                        "date": ann_date,
                        "expiration": ann_expiration,
                        "announcement": f"{announcement}",
                        "type": f"{ann_type}",
                    },
                    "website": {
                        "date": ann_date,
                        "expiration": ann_expiration,
                        "announcement": f"{announcement}",
                        "type": f"{ann_type}",
                    },
                }
            else:
                announcements_json = {
                    "app": {
                        "date": ann_date,
                        "expiration": ann_expiration,
                        "announcement": f"{announcement}",
                        "type": f"{ann_type}",
                    },
                    "website": {
                        "date": ann_date,
                        "expiration": ann_expiration,
                        "announcement": f"{announcement}",
                        "type": f"{ann_type}",
                    },
                }

        json_content = json.dumps(announcements_json, indent=4)
        repo.update_file(
            content.path, f"{version_date()}", json_content, content.sha, branch="main"
        )

    elif type == "changelog":
        mainversion, miniversion = version

        item_json = {
            "version": f"{mainversion}.{miniversion}",
            "new_features": cl_features,
            "modifications": cl_modifications,
            "bug_fixes": cl_bugfixes,
        }
        changelog_json["changelog"].append(item_json)
        changelog_json["changelog"].sort(
            key=lambda x: tuple(map(int, x["version"].split("."))), reverse=True
        )

        json.dumps(changelog_json, indent=4)
        temp_json = Path("tmp/temp_json.json")
        with open(temp_json, "w+", encoding="utf-8") as f:
            json.dump(changelog_json, f, ensure_ascii=False, indent=4)
            f.seek(0)
            json_content = f.read()

        repo.update_file(
            content.path, f"{version_date()}", json_content, content.sha, branch="main"
        )

        temp_json.unlink()

        updated_json = True
        return updated_json

    else:
        mainversion, miniversion = version

        json_content = {"version": f"{mainversion}", "miniversion": f"{miniversion}"}
        json_content = json.dumps(json_content, indent=4)
        repo.update_file(
            content.path, f"{version_date()}", json_content, content.sha, branch="main"
        )

        updated_json = True
        return updated_json

    if type in ["app", "theme"]:

        # uuid = generate_uuid_string()

        if title in itemlist:
            new_item = False
        else:
            new_item = True

        if new_item:
            if type == "app":
                download_link = f"https://github.com/Droptop-Four/{community_apps_repo}/raw/main/Apps/{rmskin_name.replace(' ', '%20')}"
                image_link = f"https://raw.githubusercontent.com/Droptop-Four/{global_data_repo}/main/data/community_apps/img/{image_name}.webp"
            else:
                download_link = f"https://github.com/Droptop-Four/{community_themes_repo}/raw/main/Themes/{rmskin_name.replace(' ', '%20')}"
                image_link = f"https://raw.githubusercontent.com/Droptop-Four/{global_data_repo}/main/data/community_themes/img/{image_name}.webp"

            item_id = max(idlist) + 1

            if not description:
                description = ""
            if not version:
                version = ""
            if not author_link:
                author_link = ""
            if not github_repo:
                github_repo = ""

            if type == "app":
                item_json = {
                    "app": {
                        "id": item_id,
                        "uuid": uuid,
                        "name": title,
                        "author": author,
                        "author_id": authorised_members[2],
                        "author_link": author_link,
                        "desc": description,
                        "version": version,
                        "official_link": github_repo,
                        "direct_download_link": download_link,
                        "secondary_link": "",
                        "image_url": image_link,
                        "authorised_members": authorised_members,
                        "hidden": 0,
                        "changelog": [],
                    }
                }

                app_tags = item_json["app"]
                if changenotes:
                    app_tags["changelog"].append(
                        {"version": version, "changenotes": changenotes}
                    )

                    app_tags["changelog"].sort(key=lambda x: x["version"], reverse=True)
                else:
                    app_tags["changelog"] = []

                community_json["apps"].append(item_json)
                community_json["apps"].sort(key=lambda x: x["app"]["id"], reverse=True)

            else:
                uuid = generate_uuid_string()
                item_json = {
                    "theme": {
                        "id": item_id,
                        "uuid": uuid,
                        "name": title,
                        "author": author,
                        "author_id": authorised_members[2],
                        "author_link": author_link,
                        "desc": description,
                        "version": version,
                        "official_link": github_repo,
                        "direct_download_link": download_link,
                        "secondary_link": "",
                        "image_url": image_link,
                        "authorised_members": authorised_members,
                        "hidden": 0,
                        "changelog": [],
                    }
                }

                theme_tags = item_json["theme"]
                if changenotes:
                    theme_tags["changelog"].append(
                        {"version": version, "changenotes": changenotes}
                    )

                    theme_tags["changelog"].sort(
                        key=lambda x: x["version"], reverse=True
                    )
                else:
                    theme_tags["changelog"] = []

                community_json["themes"].append(item_json)
                community_json["themes"].sort(
                    key=lambda x: x["theme"]["id"], reverse=True
                )

            json.dumps(community_json, indent=4)
            temp_json = Path("tmp/temp_json.json")
            with open(temp_json, "w+", encoding="utf-8") as f:
                json.dump(community_json, f, ensure_ascii=False, indent=4)
                f.seek(0)
                json_content = f.read()

            if type == "app":
                repo.update_file(
                    content.path,
                    f"{version_date()}",
                    json_content,
                    content.sha,
                    branch="main",
                )
            else:
                repo.update_file(
                    content.path,
                    f"{version_date()}",
                    json_content,
                    content.sha,
                    branch="main",
                )

            temp_json.unlink()

        updated_json = True
        return updated_json, download_link, image_link, item_id, uuid


def json_edit(
    private_key,
    type,
    uuid,
    *,
    author=None,
    description=None,
    author_link=None,
    github_repo=None,
    authorised_members=None,
):
    """
    Edits the specified app or theme

    Args:
            private_key (str): The authentication private_key
            type (str): The type of package [app, theme]
            uuid (str): The uuid of the app/theme
            author (str): The author of the package
            description (str): The description of the package
            author_link (str): The link of the author
            github_repo (str): The link of the repo
            authorised_members (list): A list of authorised members to edit apps/themes

    Returns:
            edited_json (bool): If the json was edited
            download_link: The download link of the app/theme
            image_link: The image link of the app/theme
            item_id: The id of the app/theme
    """

    g, all_files = initialize_github(private_key)

    repo = g.get_repo(f"Droptop-Four/{global_data_repo}")

    if type == "app":
        content = repo.get_contents("data/community_apps/community_apps.json")
        community_json = github_reader(
            private_key, "data/community_apps/community_apps.json"
        )

        for item in community_json["apps"]:
            app_tags = item["app"]

            if app_tags["uuid"] == uuid:
                if not author:
                    author = app_tags["author"]
                if not description:
                    description = app_tags["desc"]
                if not author_link:
                    author_link = app_tags["author_link"]
                if not github_repo:
                    github_repo = app_tags["official_link"]

                app_tags["author"] = author
                app_tags["desc"] = description
                app_tags["author_link"] = author_link
                app_tags["official_link"] = github_repo

                if authorised_members:
                    for member in authorised_members:
                        if member not in app_tags["authorised_members"]:
                            app_tags["authorised_members"].append(member.id)
                else:
                    app_tags["authorised_members"] = app_tags["authorised_members"]

                json.dumps(community_json, indent=4)
                temp_json = Path("tmp/community_apps.json")
                with open(temp_json, "w+", encoding="utf-8") as f:
                    json.dump(community_json, f, ensure_ascii=False, indent=4)
                    f.seek(0)
                    json_content = f.read()
                repo.update_file(
                    content.path,
                    f"{version_date()}",
                    json_content,
                    content.sha,
                    branch="main",
                )
                download_link = app_tags["direct_download_link"]
                image_link = app_tags["image_url"]
                item_id = app_tags["id"]
                temp_json.unlink()
                break

    elif type == "theme":
        content = repo.get_contents("data/community_themes/community_themes.json")
        community_json = github_reader(
            private_key, "data/community_themes/community_themes.json"
        )

        for item in community_json["themes"]:
            theme_tags = item["theme"]

            if theme_tags["uuid"] == uuid:
                if not author:
                    author = theme_tags["author"]
                if not description:
                    description = theme_tags["desc"]
                if not author_link:
                    author_link = theme_tags["author_link"]
                if not github_repo:
                    github_repo = theme_tags["official_link"]

                theme_tags["author"] = author
                theme_tags["desc"] = description
                theme_tags["author_link"] = author_link
                theme_tags["official_link"] = github_repo

                if authorised_members:
                    for member in authorised_members:
                        if member not in theme_tags["authorised_members"]:
                            theme_tags["authorised_members"].append(member.id)
                else:
                    theme_tags["authorised_members"] = theme_tags["authorised_members"]

                json.dumps(community_json, indent=4)
                temp_json = Path("tmp/community_themes.json")
                with open(temp_json, "w+", encoding="utf-8") as f:
                    json.dump(community_json, f, ensure_ascii=False, indent=4)
                    f.seek(0)
                    json_content = f.read()
                repo.update_file(
                    content.path,
                    f"{version_date()}",
                    json_content,
                    content.sha,
                    branch="main",
                )
                download_link = theme_tags["direct_download_link"]
                image_link = theme_tags["image_url"]
                item_id = theme_tags["id"]
                temp_json.unlink()
                break

    edited_json = True
    return edited_json, download_link, image_link, item_id


def rmskin_delete(private_key, type, name):
    """
    Deletes the specified app or theme rmskin package

    Args:
            private_key (str): The authentication private_key
            type (str): The type of package [app, theme]
            name (str): The name of the app/theme
    """

    g, all_files = initialize_github(private_key)

    if type == "app":
        repo = g.get_repo(f"Droptop-Four/{community_apps_repo}")
        git_prefix = "Apps/"
        package_name = name + " (Droptop App).rmskin"
    else:
        repo = g.get_repo(f"Droptop-Four/{community_themes_repo}")
        git_prefix = "Themes/"
        package_name = name + " (Droptop Theme).rmskin"
    git_file = git_prefix + package_name
    contents = repo.get_contents(git_file, ref="main")
    repo.delete_file(contents.path, f"{version_date()}", contents.sha, branch="main")


def image_delete(private_key, type, name):
    """
    Deletes the specified app or theme image

    Args:
            private_key (str): The authentication private_key
            type (str): The type of package [app, theme]
            name (str): The name of the app/theme
    """

    g, all_files = initialize_github(private_key)

    repo = g.get_repo(f"Droptop-Four/{global_data_repo}")
    if type == "app":
        git_prefix = "data/community_apps/img/"
        package_name = name.replace(" - ", "-")
        package_name = package_name.replace(" ", "_") + ".webp"
    else:
        git_prefix = "data/community_themes/img/"
        package_name = name.replace(" - ", "-")
        package_name = package_name.replace(" ", "_") + ".webp"
    git_file = git_prefix + package_name
    contents = repo.get_contents(git_file, ref="main")
    repo.delete_file(contents.path, f"{version_date()}", contents.sha, branch="main")


def json_delete(private_key, type, uuid):
    """
    Deletes the specified app or theme from its json file

    Args:
            private_key (str): The authentication private_key
            type (str): The type of package [app, theme]
            uuid (str): The uuid of the app/theme
    """

    g, all_files = initialize_github(private_key)

    repo = g.get_repo(f"Droptop-Four/{global_data_repo}")
    if type == "app":
        content = repo.get_contents("data/community_apps/community_apps.json")
        community_json = github_reader(
            private_key, "data/community_apps/community_apps.json"
        )
        for i in range(len(community_json["apps"])):
            if community_json["apps"][i]["app"]["uuid"] == uuid:
                community_json["apps"].pop(i)
                json.dumps(community_json, indent=4)
                temp_json = Path("tmp/community_apps.json")
                with open(temp_json, "w+", encoding="utf-8") as f:
                    json.dump(community_json, f, ensure_ascii=False, indent=4)
                    f.seek(0)
                    json_content = f.read()
                repo.update_file(
                    content.path,
                    f"{version_date()}",
                    json_content,
                    content.sha,
                    branch="main",
                )
                temp_json.unlink()
                break
    else:
        content = repo.get_contents("data/community_themes/community_themes.json")
        community_json = github_reader(
            private_key, "data/community_themes/community_themes.json"
        )
        for i in range(len(community_json["themes"])):
            if community_json["themes"][i]["theme"]["uuid"] == uuid:
                community_json["themes"].pop(i)
                json.dumps(community_json, indent=4)
                temp_json = Path("tmp/community_themes.json")
                with open(temp_json, "w+", encoding="utf-8") as f:
                    json.dump(community_json, f, ensure_ascii=False, indent=4)
                    f.seek(0)
                    json_content = f.read()
                repo.update_file(
                    content.path,
                    f"{version_date()}",
                    json_content,
                    content.sha,
                    branch="main",
                )
                temp_json.unlink()
                break
