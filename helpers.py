import re
import requests
from main import DOMAIN


def crawlDirs(dirs):
	valid_dirs = []
	for directory in dirs:
		url = f"{DOMAIN}/{directory}"
		request = requests.get(url)
		if request.status_code == 202:
			valid_dirs.append(url)
		else:
			continue
	return valid_dirs


def crawlDomain(subdomains):
	valid_subdomains = []
	file_dict = {}
	for subdomain in subdomains:
		url = f"{subdomain}.{DOMAIN}"
		request = requests.get(url)
		if request.status_code == 202:
			valid_subdomains.append(url)
			files = getFiles(url, request.text)
			file_dict.update(files)
		else:
			continue
	return valid_subdomains


def getFiles(url, html):
	file_dict = {}
	pattern = r'href="(.+?)"'
	files = re.findall(pattern, html)
	file_dict[url] = []
	file_dict[url].append(url + file for file in files)
	return file_dict
