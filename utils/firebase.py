import firebase_admin
from firebase_admin import credentials, storage
import threading, requests

from pathlib import Path


def initialize_firebase(creds, logger):
	"""
	Initializes the connection with firebase.
	
	Args:
		creds (dict): The credentials for initializing the connection
		logger (logger): The logger

	Returns:
		bool: If the connection was initialized
		None/error: If the connection was initialized, None; if not, the error
	"""
	
	try:
		cred = credentials.Certificate(creds)
		firebase_admin.initialize_app(cred)
		logger.info("Connection to firebase successfully initialized")
		return True, ""
		
	except Exception as e:
		logger.critical(f"Connection to firebase failed!\n{e}")
		return False, e


def post_webhook(url, title, message):
	"""
	Sends the webhook to discord server.

	Args:
		url (str): The url of the discord webhook
		title (str): The title of the embed to send
		message (str): The message of the embed to send
	"""
	
	data = {
		"username": "Droptop Alpha",
		"embeds": [
			{
				"title": title,
				"description": message,
			}
		]
	}
	requests.post(url, json=data)


def upload_file(file, bucket_url):
	"""
	Uploads the file to firebase storage.

	Args:
		file (str): The file to upload to firebase
		bucket_url (str): The url of the firebase bucket

	Returns:
		success (bool): If the uploading succeded or not
	"""
	
	print(f"Uploading file {file}...")
	bucket = storage.bucket(bucket_url)
	
	blob = bucket.blob(file)
	print("Uploading...")
	try:
		blob.upload_from_filename(f"tmp/{file}", timeout=300)
		print("Uploaded successfully")
		success = True
		
	except Exception as e:
		print(f"Failed to upload file: {e}")
		success = False

	if success:
		try:
			blob.make_public()
		except:
			pass
		url = blob.public_url
		print(url)
		print("---\n")

	return success


def sync_files_thread(files, names, bucket_url, webhook_url):
	"""
	Syncs files with firebase, thread.

	Args:
		files (list): The list of files to use
		names (list): The list of names to use
		bucket_url (str): The url of the firebase bucket
		webhook_url (str): The url of the discord webhook
	"""
	
	file_names = []
	done = 0
	
	for i in range(len(files)):
		r = requests.get(files[i])
		filename = Path(f"tmp/{names[i]}")
		file_names.append(filename)
		f = open(filename,'wb')
		f.write(r.content)
		print(f"File {names[i]} scaricato")
		
	for i in range(len(names)):
		status = upload_file(names[i], bucket_url)
		if status:
			done = done + 1

	for file in file_names:
		file.unlink()

	if done == 2:
		post_webhook(webhook_url, "Files synced", "The files are successfully synced on firebase for the alternative download")
	elif done == 1:
		post_webhook(webhook_url, "WARNING", "One file was not correctly uploaded, the packages versions might be outdated. Run again the sync_firebase command")
	else:
		post_webhook(webhook_url, "ERROR", "The files couldn't be uploaded to firebase, the packages versions might be outdated. Run again the sync_firebase command")


def sync_files(files, names, bucket_url, webhook_url):
	"""
	Syncs files with firebase.

	Args:
		files (list): The list of files to use
		names (list): The list of names to use
		bucket_url (str): The url of the firebase bucket
		webhook_url (str): The url of the discord webhook
	"""
	
	thread = threading.Thread(target=sync_files_thread, args=(files, names, bucket_url, webhook_url))
	thread.start()
