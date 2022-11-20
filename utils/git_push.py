import github
import os, json
from utils import github_reader
import pymongo
from pymongo import MongoClient

from pathlib import Path


def git_auth():
	"""
 	Initializes github session
 	"""
	
	cluster = MongoClient(os.getenv("mongodb_id"))
	db = cluster[os.getenv("db_cluster")]
	config_collection = db["Config"]
	
	configs = config_collection.find_one({},{"_id": 0})
	github_token = configs['github_token']
	
	g = github.Github(github_token)
	all_files = []
	return g, all_files



def push_rmskin(type, title, author, package_name, version=None, ):
	"""
 	Pushes the rmskin package to github

  	Args:
   		type (str): The type of package [app, theme]
  		title (str): The title of the package
  		author (str): The author of the package
  		version (str): The version of the package
  		package_name (str): The name of the package

 	Returns:
 		creation (bool): if the package was created (True) or it was already present and was only updated (False)
 	"""

	g, all_files = git_auth()
	if type == "app":
		#repo = g.get_repo("Droptop-Four/test")
		repo = g.get_repo("Droptop-Four/Droptop-Community-Apps")
		git_prefix = 'Apps/'
	else:
		#repo = g.get_repo("Droptop-Four/test")
		repo = g.get_repo("Droptop-Four/Droptop-Community-Themes")
		git_prefix = 'Themes/'
	
	contents = repo.get_contents("")

	while contents:
		file_content = contents.pop(0)
		if file_content.type == "dir":
			contents.extend(repo.get_contents(file_content.path))
		else:
			file = file_content
			all_files.append(str(file).replace('ContentFile(path="','').replace('")',''))

	with open(f'tmp/{package_name}.rmskin', 'rb') as file:
		content = file.read()

	git_file = git_prefix + package_name + ".rmskin"
	
	if git_file in all_files:
		contents = repo.get_contents(git_file)
		if type == "app":
			repo.update_file(contents.path, f"Update {title}-{author}-v{version}", content, contents.sha, branch="main")
		else:
			repo.update_file(contents.path, f"Update {title}-{author}", content, contents.sha, branch="main")
		creation = False
		return creation
	
	else:
		if type == "app":
			repo.create_file(git_file, f"Release {title}-{author}-v{version}", content, branch="main")
		else:
			repo.create_file(git_file, f"Release {title}-{author}", content, branch="main")
		creation = True
		return creation



def push_image(type, title, author, image_name, version=None):
	"""
 	Pushes the image to github

  	Args:
   		type (str): The type of package [app, theme]
  		title (str): The title of the package
  		author (str): The author of the package
		version (str): The version of the package
		image_name (str): The name of the image
  
 	Returns:
 		creation (bool): if the image was created (True) or it was already present and was only updated (False)
 	"""

	g, all_files = git_auth()
	#repo = g.get_repo("Droptop-Four/test")
	repo = g.get_repo("Droptop-Four/GlobalData")
	
	if type == "app":
		git_prefix = 'data/community_apps/img/'
	else:
		git_prefix = 'data/community_themes/img/'
	
	contents = repo.get_contents("")

	while contents:
		file_content = contents.pop(0)
		if file_content.type == "dir":
			contents.extend(repo.get_contents(file_content.path))
		else:
			file = file_content
			all_files.append(str(file).replace('ContentFile(path="','').replace('")',''))

	with open(f'tmp/{image_name}.webp', 'rb') as file:
		content = file.read()
	
	git_file = git_prefix + image_name + ".webp"
	
	if git_file in all_files:
		contents = repo.get_contents(git_file)
		if type == "app":
			repo.update_file(contents.path, f"Update {title}-{author}-v{version}", content, contents.sha, branch="main")
		else:
			repo.update_file(contents.path, f"Update {title}-{author}", content, contents.sha, branch="main")
		creation = False
		return creation
	
	else:
		if type == "app":
			repo.create_file(git_file, f"Release {title}-{author}-v{version}", content, branch="main")
		else:
			repo.create_file(git_file, f"Release {title}-{author}", content, branch="main")
		creation = True
		return creation




def update_json(type, title=None, author=None, description=None, rmskin_name=None, image_name=None, version=None):
	"""
	Updates the json file with the new package information

 	Args:
  		type (str): The type of package [app, theme]
  		title (str): The title of the package
  		author (str): The author of the package
		version (str): The version of the package
  		description (str): The description of the package
		rmskin_name (str): The name of the rmskin package
		image_name (str): The name of the image

	Returns:
		creation (bool): if the app inside of the json was created (True) or it was already present and was only updated (False)
 	"""


	g, all_files = git_auth()

	repo = g.get_repo("Droptop-Four/GlobalData")
	#repo = g.get_repo("Droptop-Four/test")

	if type == "app":
		content = repo.get_contents("data/community_apps/community_apps.json")
		community_json = github_reader("data/community_apps/community_apps.json")
	elif type == "theme":
		content = repo.get_contents("data/community_themes/community_themes.json")
		community_json = github_reader("data/community_themes/community_themes.json")
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
			if app_tags["name"] == title and version != app_tags["version"]:
				app_tags["version"] = version
				json.dumps(community_json, indent=4)
				temp_json = Path("tmp/community_apps.json")
				with open(temp_json, 'w+', encoding='utf-8') as f:
					json.dump(community_json, f, ensure_ascii=False, indent=4)
					f.seek(0)
					json_content = f.read()
				repo.update_file(content.path, f"Update {title}-{author}-{version}", json_content, content.sha, branch="main")
				download_link = app_tags["direct_download_link"]
				image_link = app_tags["image_url"]
				item_id = app_tags["id"]
				temp_json.unlink()
			elif app_tags["name"] == title and version == app_tags["version"]:
				download_link = app_tags["direct_download_link"]
				image_link = app_tags["image_url"]
				item_id = app_tags["id"]
			else:
				pass
	elif type == "theme":
		for item in community_json["themes"]:
			theme_tags = item["theme"]
			itemlist.append(theme_tags["name"])
			idlist.append(theme_tags["id"])
			if theme_tags["name"] == title:
				theme_tags["version"] = version
				json.dumps(community_json, indent=4)
				temp_json = Path("tmp/community_themes.json")
				with open(temp_json, 'w+', encoding='utf-8') as f:
					json.dump(community_json, f, ensure_ascii=False, indent=4)
					f.seek(0)
					json_content = f.read()
				repo.update_file(content.path, f"Update {title}-{author}", json_content, content.sha, branch="main")
				download_link = theme_tags["direct_download_link"]
				image_link = theme_tags["image_url"]
				item_id = theme_tags["id"]
				temp_json.unlink()
			elif theme_tags["name"] == title:
				download_link = theme_tags["direct_download_link"]
				image_link = theme_tags["image_url"]
				item_id = theme_tags["id"]
			else:
				pass
			
			
	else:
		json_content = {
    		"version": f"{version}"
		}
		json_content = json.dumps(json_content, indent = 4)
		repo.update_file(content.path, f"Droptop new version {version}", json_content, content.sha, branch="main")

	if type in ["app", "theme"]:
	
		if title in itemlist:
			new_item = False
		else:
			new_item = True
		
		if new_item:
			if type == "app":
				download_link = f"https://github.com/Droptop-Four/Droptop-Community-Apps/raw/main/Apps/{rmskin_name.replace(' ', '%20')}.rmskin"
				image_link = f"https://raw.githubusercontent.com/Droptop-Four/GlobalData/main/data/community_apps/img/{image_name}.webp"
			elif type == "theme":
				download_link = f"https://github.com/Droptop-Four/Droptop-Community-Themes/raw/main/Themes/{rmskin_name.replace(' ', '%20')}.rmskin"
				image_link = f"https://raw.githubusercontent.com/Droptop-Four/GlobalData/main/data/community_themes/img/{image_name}.webp"
			else:
				pass
			
			item_id = max(idlist) + 1
	
			if type == "app":
				item_json = {
					"app": {
						"id": item_id,
						"name": title,
						"author": author,
						"author_link": "#",
						"desc": description,
						"version": version,
						"official_link": "#",
						"direct_download_link": download_link,
						"secondary_link": "#",
						"image_url": image_link
					}
				}
				community_json["apps"].append(item_json)
				community_json["apps"].sort(key=lambda x: x["app"]["id"], reverse=True)
			elif type == "theme":
				if description:
					item_json = {
						"theme": {
							"id": item_id,
							"name": title,
							"author": author,
							"author_link": "#",
							"desc": description,
							"official_link": "#",
							"direct_download_link": download_link,
							"secondary_link": "#",
							"image_url": image_link
						}
					}
				else:
					item_json = {
						"theme": {
							"id": item_id,
							"name": title,
							"author": author,
							"author_link": "#",
							"desc": "#",
							"official_link": "#",
							"direct_download_link": download_link,
							"secondary_link": "#",
							"image_url": image_link
						}
					}
				community_json["themes"].append(item_json)
				community_json["themes"].sort(key=lambda x: x["theme"]["id"], reverse=True)
			else:
				pass
			
			json.dumps(community_json, indent = 4)
			temp_json = Path("tmp/temp_json.json")
			with open(temp_json, 'w+', encoding='utf-8') as f:
				json.dump(community_json, f, ensure_ascii=False, indent=4)
				f.seek(0)
				json_content = f.read()
			
			if type == "app":
				repo.update_file(content.path, f"Release {title}-{author}-v{version}", json_content, content.sha, branch="main")
			elif type == "theme":
				repo.update_file(content.path, f"Release {title}-{author}", json_content, content.sha, branch="main")
	
			temp_json.unlink()
		else:
			pass
		
		updated_json = True
	
		return updated_json, download_link, image_link, item_id

	else:
		updated_json = True
		
		return updated_json
