def version_validator(version):
	"""
	Checks if the version is written in a proper way.

	Args:
		version (str): The version to check
	
	Returns:
		is_valid (bool): True if the version is valid, False if not
	"""

	version_numbers = version.split(".")
	for element in version_numbers:
		if element.isdigit():
			if len(version_numbers[0]) == 1 and len(version_numbers[1]) == 3:
				is_valid = True
			else:
				is_valid = False
				break
		else:
			is_valid = False
			break

	return is_valid
