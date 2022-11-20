
from datetime import date, datetime
import time


def date_time():
	nowstr = datetime.now()
	datetimestr = nowstr.strftime("%d/%m/%Y %H:%M:%S")  # Day/Month/Year Hours:Minutes:Seconds
	return datetimestr

def today_date():
	today = date.today()
	return today

