import json
import requests
import os
import base64
import pymongo
from pymongo import MongoClient


from dotenv import load_dotenv

load_dotenv()


cluster = MongoClient(os.getenv("mongodb_id"))
db = cluster[os.getenv("db_cluster")]
config_collection = db["Config"]

configs = config_collection.find_one({},{"_id": 0})


def github_read_file(username, repository_name, file_path, github_token=None):
	"""
	Reads online github file and returns it as a json object.
 	
 	Args:
  		username (str): Github username
  		repository_name (str): Github repository name
  		file_path (str): Path to file on github
  		github_token (str): Github token
 	
  	Returns:
 		file_content (str): JSON object of file contents
 	"""
	
	headers = {}
	if github_token:
		headers['Authorization'] = f"token {github_token}"
	
	url = f'https://api.github.com/repos/{username}/{repository_name}/contents/{file_path}'
	r = requests.get(url, headers=headers)
	r.raise_for_status()
	data = r.json()
	file_content = data['content']
	file_content_encoding = data.get('encoding')
	if file_content_encoding == 'base64':
		file_content = base64.b64decode(file_content).decode()
	
	return file_content


def github_reader(path):
	"""
 	Reads a file from github and returns it as a json object.
	
  	Args:
  		path (str): Path to file on github
 	 	
  	Returns:
  		data: (json): JSON object of file contents
 	"""

	github_token = configs['github_token']
	username = 'Droptop-Four'
	repository_name = 'GlobalData'
	file_path = path
	file_content = github_read_file(username, repository_name, file_path, github_token=github_token)
	data = json.loads(file_content)
	return data
	#print(data)


