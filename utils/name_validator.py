

def rmskin_rename(type, title, author):
	"""
	Renames the rmskin file to the proper name
 
	Args:
		type (str): The type of package [app, theme]
		title (str): The title of the package
		author (str): The author of the package
  
	Returns:
		name (str): The new name of the package
 	"""
	
	if type == "app":
		name = title + " - " + author + " (Droptop App)"
	else:
		name = title + " - " + author + " (Droptop Theme)"
	return name



def img_rename(title, author):
	"""
	Renames the image file to the proper name
 
	Args:
		title (str): The title of the package
		author (str): The author of the package
  
	Returns:
		name (str): The new name of the image
 	"""

	name = title.replace(" ", "_") + "-" + author.replace(" ", "_")
	return name

