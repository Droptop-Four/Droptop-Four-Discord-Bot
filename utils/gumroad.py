import aiohttp
import datetime

def initialize_gumroad(token):
	"""
 	Initializes the connection with gumroad.

	Args:
		token (str): The authentication token

	Returns:
		client (GumroadClient): The gumroad instance
 	"""
	
	client = GumroadClient(secrets_dict=token)
	return client


async def get_all_sales(token, config_collection):
	"""
 	Gets the number of sales.

	Args:
		token (str): The authentication token
  		config_collection: The config collection

	Returns:
		sales (int): The number of sales
 	"""
	
	client = initialize_gumroad(token)
	sales = await client.retrieve_all_sales(config_collection)

	return sales


"""
Code took from https://github.com/opsdisk/pygumroad and made async
"""


__version__ = "0.0.3"

class GumroadClient:
	def __init__(self, secrets_dict={}, **kwargs):

		self.host = secrets_dict["gumroad"]["host"]
		self.token = secrets_dict["gumroad"]["token"]
		self.BASE_URL = f"https://{self.host}"
		self.user_agent = kwargs.get("user_agent", f"pygumroad-api-client-v{__version__}")
		self.headers = {"User-Agent": self.user_agent}
		self.payload = {"access_token": self.token}
		self.max_attempts = kwargs.get("max_attempts", 3)

	
	async def api_query(self, endpoint, **kwargs):
		"""Executes a properly formatted API call to the Gumroad API with the supplied arguments."""

		url = f"{self.BASE_URL}{endpoint}"
		headers = kwargs.get("headers", {})
		if not isinstance(headers, dict):
			raise ValueError("headers keyword passed to api_query is not a valid dict object")
		headers = {**self.headers, **headers}
		method = kwargs.get("method", "GET")
		method = method.upper()
		parameters = kwargs.get("parameters", {})
		if not isinstance(parameters, dict):
			raise ValueError("parameters keyword passed to api_query is not a valid dict object")
		payload = kwargs.get("payload", {})
		payload = {**self.payload, **payload}
		attempts = 0

		while True:
			try:
				if method == "GET":
					async with aiohttp.request('GET', url, data=payload, headers=headers) as response:
						if response.status != 200:
							debug_requests_response(response)
						else:
							json_response = await response.json()
					break
				else:
					print(f"Invalid HTTP method passed to api_query: {method}")
					raise ValueError(f"Invalid HTTP method passed to api_query: {method}")
			except (
				aiohttp.ServerTimeoutError,
				aiohttp.ClientConnectionError,
			):
				attempts += 1
				if self.max_attempts < attempts:
					print(f"Unable to reach Gumroad API after {self.max_attempts} tries.  Consider increasing the timeout.")
				else:
					print("Packet loss when attempting to reach the Gumroad API.")

		return json_response

	
	async def retrieve_all_sales(self, config_collection, payload={}, page_key=1):
		"""Retrieve all the sales given an optional payload or page"""

		configs = config_collection.find_one({},{"_id": 0})

		new_sales = 0

		payload["page_key"] = page_key

		json_response = await self.api_query(f"/v2/sales", method="GET")

		if json_response["success"] is True:
			sales = json_response["sales"]

			for sale in sales:
				d1 = datetime.datetime.strptime(sale["created_at"],"%Y-%m-%dT%H:%M:%SZ")
				new_format = "%y.%m%d%H%M%S"
				d2 = d1.strftime(new_format)
				last_date = configs["gumroad_latest_sale"]
				if float(d2) > float(last_date):
					go_on=True
					query = { "gumroad_latest_sale": last_date }
					newvalues = { "$set": { "gumroad_latest_sale": d2 } }
					config_collection.update_one(query, newvalues)
					new_sales += 1
				else:
					go_on=False
					break

		# Only runs if more than 10 sales exist, since each page only pulls back 10 at a time.
		if ("next_page_url" in json_response) and go_on:
			next_page_url = json_response["next_page_url"]
			go_on=True

			while next_page_url:
				# Update the page key.
				page_key += 1
				payload["page_key"] = page_key

				json_response = await self.api_query(f"{next_page_url}", method="GET")

				if json_response["success"] is True:
					sales = json_response["sales"]
					for sale in sales:
						d1 = datetime.datetime.strptime(sale["created_at"],"%Y-%m-%dT%H:%M:%SZ")
						new_format = "%y.%m%d%H%M%S"
						d2 = d1.strftime(new_format)
						if float(d2) > float(last_date):
							go_on=True
							query = { "gumroad_latest_sale": last_date }
							newvalues = { "$set": { "gumroad_latest_sale": d2 } }
							config_collection.update_one(query, newvalues)
							new_sales += 1
						else:
							go_on=False
							break

				if "next_page_url" in json_response:
					next_page_url = json_response["next_page_url"]
				else:
					next_page_url = None

		gumroad_sales = configs["gumroad_sales"]
		query = { "gumroad_sales": gumroad_sales }
		newvalues = { "$set": { "gumroad_sales": gumroad_sales+new_sales } }		
		config_collection.update_one(query, newvalues)

		return gumroad_sales+new_sales
	

def debug_requests_response(response):
	"""Provide debug print info for a requests response object."""

	history = response.history
	print(history)
