import firebase_admin
from firebase_admin import credentials, storage

 

def initialize_firebase(creds):

	cred = credentials.Certificate(creds)
	firebase_admin.initialize_app(cred)


def sync_files(file):

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

	return url


	

