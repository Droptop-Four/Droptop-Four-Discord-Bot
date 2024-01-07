import pygumroad

def initialize_gumroad(token):
	"""
	Initializes the connection with gumroad.
	
	Args:
		token (str): The authentication token
	
	Returns:
		client (GumroadClient): The gumroad instance
	"""
	
	client = pygumroad.GumroadClient(secrets_dict=token)
	
	return client


def get_all_sales(token):
	"""
	Gets the number of sales.
	
	Args:
		token (str): The authentication token
	
	Returns:
		sales (int): The number of sales
	"""
	
	client = initialize_gumroad(token)
	products = client.retrieve_all_products()
	sales = products[0]["sales_count"]
	
	return sales
