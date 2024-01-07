from datetime import date, datetime
import time


def date_time():
	"""
	Returns the datetime of the moment
	
	Returns:
		datetimestr (str): The datetime of the moment
	"""
	
	nowstr = datetime.now()
	datetimestr = nowstr.strftime("%d/%m/%Y %H:%M:%S")  # Day/Month/Year Hours:Minutes:Seconds
	
	return datetimestr


def today_date():
	"""
	Returns today's date
	
	Returns:
		today (date): Today's date
	"""
	
	today = date.today()
	
	return today


def version_date():
	"""
	Returns the time format as 23.0915
	
	Returns:
		string (str): The time format
	"""
	
	string = time.strftime('%y.%m%d')
	
	return string
