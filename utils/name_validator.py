import re


def rmskin_name_check(type, name):
    """
    Checks if the rmskin file has the proper name.

    Args:
            type (str): The type of package [app, theme]
            name (str): The name of the package

    Returns:
            bool: If the name is valid
    """

    if type == "app":
        pattern = r"(\w+)_-_(\w+)_Droptop_App.rmskin"
    else:
        pattern = r"(\w+)_-_(\w+)_Droptop_Theme.rmskin"
    prog = re.compile(pattern)
    result = prog.search(name)

    if result:
        return True
    else:
        return False


def rmskin_rename(type, name):
    """
    Renames the rmskin file to the proper name.

    Args:
            type (str): The type of package [app, theme]
            name (str): The name of the package

    Returns:
            name (str): The new name of the package
    """

    name = name.replace("_", " ")
    if type == "app":
        name = name.replace("Droptop App", "(Droptop App)")
    else:
        name = name.replace("Droptop Theme", "(Droptop Theme)")

    return name


def get_title_author(type, name):
    """
    Separates the title and the author from the name.

    Args:
            type (str): The type of package [app, theme]
            name (str): The name of the package

    Returns:
            title (str): The title of the package
            author (str): The author of the package
    """

    lista = name.split("_-_")
    lista2 = []
    lista3 = []

    for element in lista:
        if "_Droptop_App.rmskin" in element:
            element = element.replace("_Droptop_App.rmskin", "")
            lista2.append(element)
        elif "_Droptop_Theme.rmskin" in element:
            element = element.replace("_Droptop_Theme.rmskin", "")
            lista2.append(element)
        else:
            lista2.append(element)

    for element in lista2:
        element = element.replace("_", " ")
        lista3.append(element)

    title = lista3[0]
    author = lista3[1]

    return title, author


def img_rename(type, name):
    """
    Renames the image file to the proper name.

    Args:
            title (str): The title of the package
            author (str): The author of the package

    Returns:
            name (str): The new name of the image
    """

    name = name.replace(" ", "_")

    return name
