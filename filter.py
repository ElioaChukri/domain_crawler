import re
from test_script import DOMAIN
from logger import logger


def checkUrl(url):
	"""
	Checks if the url is valid
	:param url: str
	:return: bool
	"""

	pattern = re.compile(rf"https?://([a-zA-Z0-9-]+\.)*{DOMAIN}")
	if pattern.match(url):
		return True
	else:
		return False


def getLinks(html):
	"""
	Uses a regex to filter all the links stored in href attributes in the html
	The provided regex matches all the tags that are commonly used to link to files with the href attribute
	:param html: str
	:return new_links: list
	"""

	pattern = r'<(?:a|link|img|video|audio|link) href="(.+?)">'
	links = re.findall(pattern, html)
	new_links = [removeAfterSpace(link) for link in links]
	return new_links


def removeAfterSpace(link):
	"""
	Some file links have parameters placed after their location, separated by a whitespace.
	This regex removes everything after the whitespace. Could've easily used .split() but I need grades lol
	:param link: str
	:return new_link: str
	"""

	pattern = re.compile(r"\s.*$")
	new_link = pattern.sub("", link)
	return new_link


def cleanLink(link):
	"""
	In addition to the parameters mentioned in the previous function, some links have parameters placed after their
	location, separated by a question mark. This regex removes everything after the question mark and leaves only the
	file path
	:param link: str
	:return file: str
	"""

	pattern = re.compile(r"\?.*")
	file = pattern.sub("", link)
	return file


def getValidFiles(links):
	"""
	Checks first if the link is present on the domain we are scanning. If it is, it checks if the file has a valid
	extension. If it does, it adds it to a list of valid files
	:param links: list
	:return valid_files: list
	"""
	with open("input_files/extensions.bat", "r") as file:
		extensions = file.read().splitlines()
	valid_files = []
	for link in links:
		if DOMAIN not in link:
			continue
		else:
			file = cleanLink(link)
			if file.endswith(tuple(extensions)):
				valid_files.append(file)
	return valid_files
