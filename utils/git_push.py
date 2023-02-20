import github
import os, json
from .github_file_reader import github_reader
from .generators import generate_uuid_string
from .time_utils import push_desc

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



def push_rmskin(type, package_name):
	"""
 	Pushes the rmskin package to github

  	Args:
   		type (str): The type of package [app, theme]
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

	with open(f'tmp/{package_name}', 'rb') as file:
		content = file.read()

	git_file = git_prefix + package_name
	
	if git_file in all_files:
		contents = repo.get_contents(git_file)
		if type == "app":
			repo.update_file(contents.path, f"{push_desc()}", content, contents.sha, branch="main")
		else:
			repo.update_file(contents.path, f"{push_desc()}", content, contents.sha, branch="main")
		creation = False
		return creation
	
	else:
		if type == "app":
			repo.create_file(git_file, f"{push_desc()}", content, branch="main")
		else:
			repo.create_file(git_file, f"{push_desc()}", content, branch="main")
		creation = True
		return creation



def push_image(type, image_name):
	"""
 	Pushes the image to github

  	Args:
   		type (str): The type of package [app, theme]
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
			repo.update_file(contents.path, f"{push_desc()}", content, contents.sha, branch="main")
		else:
			repo.update_file(contents.path, f"{push_desc()}", content, contents.sha, branch="main")
		creation = False
		return creation
	
	else:
		if type == "app":
			repo.create_file(git_file, f"{push_desc()}", content, branch="main")
		else:
			repo.create_file(git_file, f"{push_desc()}", content, branch="main")
		creation = True
		return creation


def json_update(type, *, authorised_members=None, title=None, author=None, description=None, rmskin_name=None, image_name=None, version=None, author_link=None, github_repo=None):
	"""
	Updates the json file with the new package information

 	Args:
  		type (str): The type of package [app, theme]
		authorised_members (list): A list of authorised members to edit apps/themes
  		title (str): The title of the package
  		author (str): The author of the package
  		description (str): The description of the package
		rmskin_name (str): The name of the rmskin package
		image_name (str): The name of the image
  		version (str): The version of the package
		author_link (str): The link of the author
  		github_repo (str): The link of the repo
  	
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
				
				json.dumps(community_json, indent=4)
				temp_json = Path("tmp/community_apps.json")
				with open(temp_json, 'w+', encoding='utf-8') as f:
					json.dump(community_json, f, ensure_ascii=False, indent=4)
					f.seek(0)
					json_content = f.read()
				repo.update_file(content.path, f"{push_desc()}", json_content, content.sha, branch="main")
				download_link = app_tags["direct_download_link"]
				image_link = app_tags["image_url"]
				item_id = app_tags["id"]
				uuid = app_tags["uuid"]
				temp_json.unlink()
			elif app_tags["name"] == title and version == app_tags["version"]:
				
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
				
				json.dumps(community_json, indent=4)
				temp_json = Path("tmp/community_apps.json")
				with open(temp_json, 'w+', encoding='utf-8') as f:
					json.dump(community_json, f, ensure_ascii=False, indent=4)
					f.seek(0)
					json_content = f.read()
				repo.update_file(content.path, f"{push_desc()}", json_content, content.sha, branch="main")
				download_link = app_tags["direct_download_link"]
				image_link = app_tags["image_url"]
				item_id = app_tags["id"]
				uuid = app_tags["uuid"]
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
				
				json.dumps(community_json, indent=4)
				temp_json = Path("tmp/community_themes.json")
				with open(temp_json, 'w+', encoding='utf-8') as f:
					json.dump(community_json, f, ensure_ascii=False, indent=4)
					f.seek(0)
					json_content = f.read()
				repo.update_file(content.path, f"{push_desc()}", json_content, content.sha, branch="main")
				download_link = theme_tags["direct_download_link"]
				image_link = theme_tags["image_url"]
				item_id = theme_tags["id"]
				uuid = theme_tags["uuid"]
				temp_json.unlink()
			else:
				pass

	else:

		mainversion, miniversion = version
		
		json_content = {
			"version": f"{mainversion}",
			"miniversion": f"{miniversion}"
		}
		json_content = json.dumps(json_content, indent = 4)
		repo.update_file(content.path, f"{push_desc()}", json_content, content.sha, branch="main")

		updated_json = True
		return updated_json
	
	if type in ["app", "theme"]:

		uuid = generate_uuid_string()
	
		if title in itemlist:
			new_item = False
		else:
			new_item = True
		
		if new_item:
			if type == "app":
				download_link = f"https://github.com/Droptop-Four/Droptop-Community-Apps/raw/main/Apps/{rmskin_name.replace(' ', '%20')}"
				image_link = f"https://raw.githubusercontent.com/Droptop-Four/GlobalData/main/data/community_apps/img/{image_name}.webp"
			else:
				download_link = f"https://github.com/Droptop-Four/Droptop-Community-Themes/raw/main/Themes/{rmskin_name.replace(' ', '%20')}"
				image_link = f"https://raw.githubusercontent.com/Droptop-Four/GlobalData/main/data/community_themes/img/{image_name}.webp"

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
						"hidden": 0
					}
				}
				community_json["apps"].append(item_json)
				community_json["apps"].sort(key=lambda x: x["app"]["id"], reverse=True)
			
			else:
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
						"hidden": 0
					}
				}
				community_json["themes"].append(item_json)
				community_json["themes"].sort(key=lambda x: x["theme"]["id"], reverse=True)

			json.dumps(community_json, indent = 4)
			temp_json = Path("tmp/temp_json.json")
			with open(temp_json, 'w+', encoding='utf-8') as f:
				json.dump(community_json, f, ensure_ascii=False, indent=4)
				f.seek(0)
				json_content = f.read()
			
			if type == "app":
				repo.update_file(content.path, f"{push_desc()}", json_content, content.sha, branch="main")
			else:
				repo.update_file(content.path, f"{push_desc()}", json_content, content.sha, branch="main")
	
			temp_json.unlink()

		updated_json = True
		return updated_json, download_link, image_link, item_id, uuid



def json_edit(type, uuid, *, author=None, description=None, author_link=None, github_repo=None, authorised_members=None):
	"""
 	Edits the specified app or theme

   	Args:
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

	g, all_files = git_auth()

	repo = g.get_repo("Droptop-Four/GlobalData")
	#repo = g.get_repo("Droptop-Four/test")

	if type == "app":
		content = repo.get_contents("data/community_apps/community_apps.json")
		community_json = github_reader("data/community_apps/community_apps.json")

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
				with open(temp_json, 'w+', encoding='utf-8') as f:
					json.dump(community_json, f, ensure_ascii=False, indent=4)
					f.seek(0)
					json_content = f.read()
				repo.update_file(content.path, f"{push_desc()}", json_content, content.sha, branch="main")
				download_link = app_tags["direct_download_link"]
				image_link = app_tags["image_url"]
				item_id = app_tags["id"]
				temp_json.unlink()
				break
	
	elif type == "theme":
		content = repo.get_contents("data/community_themes/community_themes.json")
		community_json = github_reader("data/community_themes/community_themes.json")

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
				with open(temp_json, 'w+', encoding='utf-8') as f:
					json.dump(community_json, f, ensure_ascii=False, indent=4)
					f.seek(0)
					json_content = f.read()
				repo.update_file(content.path, f"{push_desc()}", json_content, content.sha, branch="main")
				download_link = theme_tags["direct_download_link"]
				image_link = theme_tags["image_url"]
				item_id = theme_tags["id"]
				temp_json.unlink()
				break

	edited_json = True
	return edited_json, download_link, image_link, item_id

	

def rmskin_delete(type, name):
	"""
 	Deletes the specified app or theme rmskin package

   	Args:
		type (str): The type of package [app, theme]
		name (str): The name of the app/theme
   	"""
	
	g, all_files = git_auth()
	
	if type == "app":
		#repo = g.get_repo("Droptop-Four/test")
		repo = g.get_repo("Droptop-Four/Droptop-Community-Apps")
		git_prefix = 'Apps/'
		package_name = name + " (Droptop App).rmskin"
	else:
		#repo = g.get_repo("Droptop-Four/test")
		repo = g.get_repo("Droptop-Four/Droptop-Community-Themes")
		git_prefix = 'Themes/'
		package_name = name + " (Droptop Theme).rmskin"
	git_file = git_prefix + package_name
	contents = repo.get_contents(git_file, ref="main")
	repo.delete_file(contents.path, f"{push_desc()}", contents.sha, branch="main")



def image_delete(type, name):
	"""
 	Deletes the specified app or theme image

   	Args:
		type (str): The type of package [app, theme]
		name (str): The name of the app/theme
   	"""
	
	g, all_files = git_auth()

	#repo = g.get_repo("Droptop-Four/test")
	repo = g.get_repo("Droptop-Four/GlobalData")
	if type == "app":
		git_prefix = 'data/community_apps/img/'
		package_name = name.replace(" - ", "-")
		package_name = package_name.replace(" ", "_") + ".webp"
	else:
		git_prefix = 'data/community_themes/img/'
		package_name = name.replace(" - ", "-")
		package_name = package_name.replace(" ", "_") + ".webp"
	git_file = git_prefix + package_name
	contents = repo.get_contents(git_file, ref="main")
	repo.delete_file(contents.path, f"{push_desc()}", contents.sha, branch="main")



def json_delete(type, uuid):
	"""
 	Deletes the specified app or theme from its json file

   	Args:
		type (str): The type of package [app, theme]
		uuid (str): The uuid of the app/theme
   	"""

	g, all_files = git_auth()

	repo = g.get_repo("Droptop-Four/GlobalData")
	#repo = g.get_repo("Droptop-Four/test")
	if type == "app":
		content = repo.get_contents("data/community_apps/community_apps.json")
		community_json = github_reader("data/community_apps/community_apps.json")
		for i in range(len(community_json["apps"])):
			if community_json["apps"][i]["app"]["uuid"] == uuid:
				community_json["apps"].pop(i)
				json.dumps(community_json, indent=4)
				temp_json = Path("tmp/community_apps.json")
				with open(temp_json, 'w+', encoding='utf-8') as f:
					json.dump(community_json, f, ensure_ascii=False, indent=4)
					f.seek(0)
					json_content = f.read()
				repo.update_file(content.path, f"{push_desc()}", json_content, content.sha, branch="main")
				temp_json.unlink()
				break
	else:
		content = repo.get_contents("data/community_themes/community_themes.json")
		community_json = github_reader("data/community_themes/community_themes.json")
		for i in range(len(community_json["themes"])):
			if community_json["themes"][i]["theme"]["uuid"] == uuid:
				community_json["themes"].pop(i)
				json.dumps(community_json, indent=4)
				temp_json = Path("tmp/community_themes.json")
				with open(temp_json, 'w+', encoding='utf-8') as f:
					json.dump(community_json, f, ensure_ascii=False, indent=4)
					f.seek(0)
					json_content = f.read()
				repo.update_file(content.path, f"{push_desc()}", json_content, content.sha, branch="main")
				temp_json.unlink()
				break



