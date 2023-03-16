
"""
This module contains functions that are used to filter the links and files from the html
"""

import re
from test_script import args


def checkUrl(url):
	"""
	Checks if the url is valid
	Args:
		url (str): url to be checked
	Returns:
		True if the url is valid, False otherwise
	"""

	pattern = re.compile(rf"https?://([a-zA-Z0-9-]+\.)*{args.domain}")
	if pattern.match(url):
		return True
	else:
		return False


def getLinks(html):
	"""
	Uses a regex to filter all the links stored in href attributes in the html
	The provided regex matches all the tags that are commonly used to link to files with the href attribute
	Args:
		html (str): html to be parsed
	Returns:
		new_links (list): list of links found in the html
	"""

	pattern = r'<(?:a|link|img|video|audio|link) href="(.+?)">'
	links = re.findall(pattern, html)
	new_links = [removeAfterSpace(link) for link in links]
	return new_links


def removeAfterSpace(link):
	"""
	Some file links have parameters placed after their location, separated by a whitespace.
	This regex removes everything after the whitespace. Could've easily used .split() but I need grades lol
	Args:
		link (str): link to be cleaned
	Returns:
		new_link (str): cleaned link, removing any parameters after the whitespace
	"""

	pattern = re.compile(r"\s.*$")
	new_link = pattern.sub("", link)
	return new_link


def cleanLink(link):
	"""
	In addition to the parameters mentioned in the previous function, some links have parameters placed after their
	location, separated by a question mark. This regex removes everything after the question mark and leaves only the
	file path
	Args:
		link (str): link to be cleaned
	Returns:
		file (str): cleaned link, removing any parameters after the question mark
	"""

	pattern = re.compile(r"\?.*")
	file = pattern.sub("", link)
	return file


def getValidFiles(links):
	"""
	Checks first if the link is present on the domain we are scanning. If it is, it checks if the file has a valid
	extension. If it does, it adds it to a list of valid files
	Args:
		links (list): list of links found in the html
	Returns:
		valid_files (list): list of valid files
	"""
	with open("input_files/extensions.bat", "r") as file:
		extensions = file.read().splitlines()
	valid_files = []
	for link in links:
		if args.domain not in link:
			continue
		else:
			file = cleanLink(link)
			if file.endswith(tuple(extensions)):
				valid_files.append(file)
	return valid_files
