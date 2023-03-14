from threading import current_thread
import os
import requests
from test_script import DOMAIN, count_dir, count_domain
from filter import *


def loadFiles():
	"""
	Loads the directories and subdomains from the files
	"""

	with open("input_files/dirs_dictionary.bat", "r") as f1:
		dirs = f1.read().lower().splitlines()

	with open("input_files/subdomains_dictionary.bat", "r") as f2:
		subdomains = f2.read().lower().splitlines()

	dirs = list(set(dirs))
	subdomains = list(set(subdomains))
	return dirs, subdomains


def writeFiles(valid_dirs, valid_subdomains, files):
	"""
	Writes the valid directories, subdomains, and files to the output_files directory
	If the directory output_files does not exist, it will be created
	:param valid_dirs: list
	:param valid_subdomains: list
	:param files: list
	:return: void
	"""

	directory = "output_files"
	if not os.path.exists(directory):
		os.makedirs(directory)
		logger.debug("Created directory: " + directory)

	with open("output_files/valid_dirs.bat", "w") as f1:
		for folder in valid_dirs:
			f1.write(folder + "\n")
		logger.debug("Wrote valid directories to file: " + f1.name)

	with open("output_files/valid_subdomains.bat", "w") as f2:
		for domain in valid_subdomains:
			f2.write(domain + "\n")
		logger.debug("Wrote valid subdomains to file: " + f2.name)

	with open("output_files/files.bat", "w") as f3:
		for file in files:
			f3.write(file + "\n")
		logger.debug("Wrote all all files found to file: " + f3.name)


def crawlDirs(dirs):
	"""
	Queries all the possible directories listed in the file given and returns
	a list of directories that return a 202 status code
	:param dirs: list
	:return valid_dirs: list
	"""

	valid_dirs = []
	for directory in dirs:

		count_dir.value += 1
		if count_dir.value % 100 == 0:
			logger.info(f"Checked {count_dir.value} directories")

		url = f"https://{DOMAIN}/{directory}"
		request = requests.get(url)
		if request.status_code in [200, 201, 202, 203, 204, 205, 206]:
			valid_dirs.append(url)
			logger.info(f"Found valid directory: {url}")
		else:
			continue
	return valid_dirs


def crawlDomain(subdomains):
	"""
	Queries all the possible subdomains listed in the file given and returns
	a list of subdomains that return a 202 status code
	:param subdomains: list
	:return valid_subdomains: list
	"""

	valid_subdomains = []
	for subdomain in subdomains:

		count_domain.value += 1
		logger.debug("Count is " + str(count_domain.value))
		if count_domain.value % 10000 == 0:
			logger.info(f"Checked {count_domain.value} subdomains")

		url = f"https://{subdomain}.{DOMAIN}"
		if not checkUrl(url):
			continue
		try:
			request = requests.get(url)
		except requests.exceptions.ConnectionError:
			continue
		if request.status_code in [200, 201, 202, 203, 204, 205, 206]:
			valid_subdomains.append(url)
			logger.info(f"Found valid subdomain: {url}")
		else:
			continue
	return valid_subdomains


def getFiles(url):
	"""
	Scrapes the html for files that are being linked to in the html and stores them in a list
	:param url: str
	:return files: list
	"""

	html = requests.get(url).text
	links = getLinks(html)
	files = getValidFiles(links)
	logger.debug(f"Found {len(files)} files for {url}")
	return files
