from pymongo import MongoClient


def initialize_mongodb(id, cluster, logger):
	"""
	Initializes the connection to the MongoDB database.

	Args:
		id (str): The id of the database
		cluster (str): The cluster of the database
		logger (logger): The logger

	Returns:
		bool: If the database was initialized
		collection/error: If the database was initialized, the collection; if not, the error
	"""

	try:
		client = MongoClient(id)
		db = client[cluster]
		config_collection = db["Config"]
		print("Connection to the database successfully initialized")
		logger.info("Connection to the database successfully initialized")
		return True, config_collection
		
	except Exception as e:
		print(f"Connection to the database failed! -> {e}")
		logger.critical(f"Connection to the database failed! -> {e}")
		return False, e
