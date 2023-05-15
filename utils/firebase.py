import firebase_admin
from firebase_admin import credentials, storage
import threading, requests

from pathlib import Path



def initialize_firebase(creds):
	"""
 	Initializes the connection with firebase.
 	"""

	cred = credentials.Certificate(creds)
	firebase_admin.initialize_app(cred)



class FileUploadError(Exception):
	pass



def post_webhook(url, title, message):
	data = {
		"username": "Droptop Four",
		"embeds": [
			{
				"title": title,
				"description": message,
			}
		]
	}
	requests.post(url, json=data)



def upload_file(file, url):
	print(f"Uploading file {file}...")
	bucket = storage.bucket("droptopfour-bec1e.appspot.com")
	blob = bucket.blob(file)
	
	try:
		blob.delete()
		print("Deleted existing file")
	except:
		pass
	
	blob = bucket.blob(file)
	print("Uploading...")
	try:
		blob.upload_from_filename(f"tmp/{file}")
		print("Uploaded successfully")
		
		return True
	except Exception as e:
		print(f"Failed to upload file: {e}")
		
		raise FileUploadError(f"Failed to upload file {file}") from e
		return False

	blob.make_public()
	url = blob.public_url
	print(url)
	print("---\n")
	return url



def main(files, names, url):
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
		status = upload_file(names[i], url)
		if status:
			done = done + 1

	for file in file_names:
		file.unlink()

	if done == 2:
		post_webhook(url, "Files synced", "The files are successfully synced on firebase for the alternative download")
	elif done == 1:
		post_webhook(url, "WARNING", "One file was not correctly uploaded, and the alternative links might not work. Run again the sync_firebase command")
	else:
		post_webhook(url, "ERROR", "The files couldn't be uploaded to firebase, and the alternative link will not work. Run again the sync_firebase command")



def sync_files(files, names, url):
	"""
	Syncs files with firebase
	"""
	
	thread = threading.Thread(target=main, args=(files, names, url))
	thread.start()
