import json
import os
import re
import requests
from main import DOMAIN


def loadFiles():
	with open("input_files/dirs_dictionary.bat", "r") as f1:
		dirs = f1.read().splitlines()

	with open("input_files/subdomains_dictionary.bat") as f2:
		subdomains = f2.read().splitlines()

	return dirs, subdomains


def writeFiles(valid_dirs, valid_subdomains, file_dict):
	directory = "output_files"
	if not os.path.exists(directory):
		os.makedirs(directory)

	with open("output_files/valid_dirs.bat", "w") as f1:
		for folder in valid_dirs:
			f1.write(folder + "\n")

	with open("output_files/valid_subdomains.bat", "w") as f2:
		for folder in valid_subdomains:
			f2.write(folder + "\n")

	with open("output_files/files.bat", "w") as f3:
		json.dump(file_dict, f3, indent=4)


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
	return valid_subdomains, file_dict


def getFiles(url, html):
	file_dict = {}
	pattern = r'href="(.+?)"'
	files = re.findall(pattern, html)
	file_dict[url] = []
	file_dict[url].append(url + file for file in files)
	return file_dict
