import logging

from pymongo import MongoClient

_logger = logging.getLogger(__name__)


def initialize_mongodb(id, cluster):
    """
    Initializes the connection to the MongoDB database.

    Args:
        id (str): The id of the database
        cluster (str): The cluster of the database

    Returns:
        bool: If the database was initialized
        config_collection/e: If the database was initialized, the config_collection; if not, the error
    """

    try:
        client = MongoClient(id)
        db = client[cluster]
        config_collection = db["Config"]
        # print("Connection to the database successfully initialized")
        _logger.info("Connection to the database successfully initialized")
        return True, config_collection

    except Exception as e:
        # print(f"Connection to the database failed! -> {e}")
        _logger.critical(f"Connection to the database failed! -> {e}")
        return False, e
