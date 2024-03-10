import logging

import fitz
import pygumroad

_logger = logging.getLogger(__name__)


def initialize_gumroad(token):
    """
    Initializes the connection with gumroad.

    Args:
        token (str): The authentication token

    Returns:
        client (GumroadClient): The gumroad instance
    """
    try:
        client = pygumroad.GumroadClient(secrets_dict=token)
    except Exception as e:
        _logger.critical(f"Connection to gumroad failed! -> {e}")
        client = None

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


def order_exists(token, order_id):
    """
    Returns whether the order exists.

    Args:
        order_id (int): The order id

    Returns:
        exists (bool): Whether the order exists
        name (str): The name of the buyer
    """

    client = initialize_gumroad(token)
    sale = client.retrieve_sales({"order_id": order_id})

    if len(sale) > 0:
        exists = True
        if "full_name" in sale[0]:
            name = f"{sale[0]['full_name']} ({sale[0]['email']})"
        else:
            name = f"{sale[0]['email'].split('@')[0]} ({sale[0]['email']})"
    else:
        exists = False
        name = ""

    return exists, name


def analyze_invoice(token, invoice):
    """
    Analyzes a pdf invoice

    Args:
        token (str): The authentication token
        invoice (Path): The invoice

    Returns:
        exists (bool): Whether the order exists
        name (str): The name of the buyer
    """

    doc = fitz.open(invoice)
    page = doc[0]
    text = page.get_text("blocks", sort=False)

    order_number = text[13][4].strip()

    if order_number.isnumeric():
        exists, name = order_exists(token, int(order_number))

    else:
        exists, name = False, ""

    return exists, name
