import logging
import threading
from pathlib import Path

import firebase_admin
import requests
from firebase_admin import credentials, storage

_logger = logging.getLogger(__name__)


def initialize_firebase(creds):
    """
    Initializes the connection with Firebase.

    Args:
        creds (dict): The credentials for initializing the connection

    Returns:
        bool: If the connection was initialized
        None/e: If the connection was initialized, None; if not, the error
    """

    try:
        cred = credentials.Certificate(creds)
        firebase_admin.initialize_app(cred)
        _logger.info("Connection to Firebase successfully initialized")
        return True, None

    except Exception as e:
        _logger.critical(f"Connection to Firebase failed!\n{e}")
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
        "username": "Droptop Four",
        "embeds": [
            {
                "title": title,
                "description": message,
            }
        ],
    }
    requests.post(url, json=data)


def upload_file(file, bucket_url):
    """
    Uploads the file to Firebase storage.

    Args:
        file (str): The file to upload to Firebase
        bucket_url (str): The url of the Firebase bucket

    Returns:
        success (bool): If the uploading succeded or not
    """

    _logger.info(f"Uploading file {file}...")
    bucket = storage.bucket(bucket_url)

    blob = bucket.blob(file)
    try:
        blob.upload_from_filename(f"tmp/{file}", timeout=300)
        _logger.info("Uploaded successfully")
        success = True

    except Exception as e:
        _logger.error(f"Failed to upload file: {e}")
        success = False

    if success:
        try:
            blob.make_public()
        except:
            pass
        # url = blob.public_url

    return success


def sync_files_thread(files, names, bucket_url, webhook_url):
    """
    Syncs files with Firebase, thread.

    Args:
        files (list): The list of files to use
        names (list): The list of names to use
        bucket_url (str): The url of the Firebase bucket
        webhook_url (str): The url of the discord webhook
    """

    file_names = []
    done = 0

    for i in range(len(files)):
        r = requests.get(files[i])
        filename = Path(f"tmp/{names[i]}")
        file_names.append(filename)
        f = open(filename, "wb")
        f.write(r.content)
        print(f"File {names[i]} scaricato")

    for i in range(len(names)):
        status = upload_file(names[i], bucket_url)
        if status:
            done = done + 1

    for file in file_names:
        file.unlink()

    if done == 2:
        post_webhook(
            webhook_url,
            "Files synced",
            "The files are successfully synced on Firebase for the alternative download",
        )
    elif done == 1:
        post_webhook(
            webhook_url,
            "WARNING",
            "One file was not correctly uploaded, the packages versions might be outdated. Run again the sync_firebase command",
        )
    else:
        post_webhook(
            webhook_url,
            "ERROR",
            "The files couldn't be uploaded to Firebase, the packages versions might be outdated. Run again the sync_firebase command",
        )


def sync_files(files, names, bucket_url, webhook_url):
    """
    Syncs files with Firebase.

    Args:
        files (list): The list of files to use
        names (list): The list of names to use
        bucket_url (str): The url of the Firebase bucket
        webhook_url (str): The url of the discord webhook
    """

    thread = threading.Thread(
        target=sync_files_thread, args=(files, names, bucket_url, webhook_url)
    )
    thread.start()
