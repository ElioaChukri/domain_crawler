import re
from test_script import DOMAIN
from logger import logger


def checkUrl(url):
	pattern = re.compile(rf"https?://([a-zA-Z0-9-]+\.)*{DOMAIN}")
	if pattern.match(url):
		return True
	else:
		return False


def getLinks(html):
	pattern = r'<(?:a|link|img|video|audio|link) href="(.+?)">'
	links = re.findall(pattern, html)
	new_links = [removeAfterSpace(link) for link in links]
	return new_links


def removeAfterSpace(link):
	pattern = re.compile(r"\s.*$")
	new_link = pattern.sub("", link)
	return new_link


def cleanLink(link):
	pattern = re.compile(r"\?.*")
	file = pattern.sub("", link)
	return file


def getValidFiles(links):
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
