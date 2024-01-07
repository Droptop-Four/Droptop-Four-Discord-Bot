from PIL import Image


def to_webp(source):
	"""
	Convert image to Webp.
	
	Args:
		source (pathlib.Path): Path to source image
	
	Returns:
		destination (pathlib.Path): Path to new image
	"""
	
	destination = source.with_suffix(".webp")
	image = Image.open(source)
	image.save(destination, format="webp")
	source.unlink()
	
	return destination
