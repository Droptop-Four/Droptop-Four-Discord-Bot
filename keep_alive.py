import logging
import subprocess
import sys
from threading import Thread

from flask import Flask


SYNTAX = "Syntax: python {0} <script>"


flask: Flask = Flask("keep_alive")
log: logging.Logger = logging.getLogger("werkzeug")


@flask.route("/")
def index() -> str:
	"""
	Method for handling the base route of "/".
	"""

	message = "Keeping the repl alive!"
	
	return message


def keep_alive() -> None:
	"""
	Wraps the web server run() method in a Thread object and starts the web server.
	"""
	
	def run() -> None:
		log.setLevel(logging.ERROR)
		flask.run(host = "0.0.0.0", port = 8080)
	thread = Thread(target = run)
	thread.start()


if __name__ == "__main__":
	if len(sys.argv) != 2:
		print(SYNTAX.format(sys.argv[0]), file = sys.stderr)
	else:
		keep_alive()
		subprocess.call(["python", sys.argv[1]])
