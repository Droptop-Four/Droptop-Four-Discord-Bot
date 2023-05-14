import firebase_admin
from firebase_admin import credentials, storage
import threading, requests

from pathlib import Path


def initialize_firebase(creds):

	cred = credentials.Certificate(creds)
	firebase_admin.initialize_app(cred)


def upload_file(file):
	print(f"Upload file {file}")
	bucket = storage.bucket("droptopfour-bec1e.appspot.com")
	blob = bucket.blob(file)
	try:
		blob.delete()
	except:
		pass
	blob = bucket.blob(file)
	blob.upload_from_filename(f"tmp/{file}")
	blob.make_public()
	url = blob.public_url
	print(url)
	print("---\n")
	return url


def main(files, names):
	file_names = []
	
	for i in range(len(files)):
		r = requests.get(files[i])
		filename = Path(f"tmp/{names[i]}")
		file_names.append(filename)
		f = open(filename,'wb')
		f.write(r.content)
		print(f"File {names[i]} scaricato")
		
	for i in range(len(names)):
		upload_file(names[i])

	for file in file_names:
		file.unlink()
	

def sync_files(files, names):
	
	thread = threading.Thread(target=main, args=(files,names))
	thread.start()


	

