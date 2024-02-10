import datetime


def validate_date(date):
    """
    Checks if the date is valid.

    Args:
            date (str): The date to check

    Returns:
            bool: If the date is valid or not
    """

    try:
        datetime.datetime.strptime(date, "%d/%m/%y")
        return True
    except ValueError:
        return False
