from threading import current_thread
from logger import logger
import json
import os
import re
import requests
from test_script import DOMAIN


def loadFiles():

	"""
	Loads the directories and subdomains from the files
	"""

	with open("input_files/dirs_dictionary.bat", "r") as f1:
		dirs = f1.read().splitlines()

	with open("input_files/subdomains_dictionary.bat", "r") as f2:
		subdomains = f2.read().splitlines()

	return dirs, subdomains


def writeFiles(valid_dirs, valid_subdomains, file_dict):

	"""
	Writes the valid directories, subdomains, and files to the output_files directory
	If the directory output_files does not exist, it will be created
	:param valid_dirs:
	:param valid_subdomains:
	:param file_dict:
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
		for folder in valid_subdomains:
			f2.write(folder + "\n")
		logger.debug("Wrote valid subdomains to file: " + f2.name)

	with open("output_files/files.bat", "w") as f3:
		json.dump(file_dict, f3, indent=4)
		logger.debug("Wrote files to file: " + f3.name)


def crawlDirs(dirs):

	"""
	Queries all the possible directories listed in the file given and returns
	a list of directories that return a 202 status code
	:param dirs: list
	:return valid_dirs: list
	"""

	thread_number = str(current_thread().name[-1])
	valid_dirs = []
	count = 0
	for directory in dirs:

		count += 1
		if count % 100 == 0:
			logger.info(f"Checked {count} directories in thread number {thread_number}")

		url = f"https://{DOMAIN}/{directory}"
		request = requests.get(url)
		if request.status_code == 202:
			valid_dirs.append(url)
			logger.info(f"Found valid directory: {url} on thread number {thread_number}")
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

	thread_number = str(current_thread().name[-1])
	valid_subdomains = []
	file_dict = {}
	count = 0
	logger.info(f"Starting subdomain crawl on thread number  {thread_number}")
	for subdomain in subdomains:

		count += 1
		if count % 100 == 0:
			logger.info(f"Checked {count} subdomains on thread number {thread_number}")

		url = f"https://{subdomain}.{DOMAIN}"
		if int(thread_number) == 1:
			logger.info(f"Checking {url} on thread number 1")
		try:
			request = requests.get(url)
			logger.debug("Requesting: " + url)
		except requests.exceptions.ConnectionError:
			logger.debug("Connection error for: " + url)
			continue
		if request.status_code == 202:
			valid_subdomains.append(url)
			logger.info(f"Found valid subdomain: {url} on thread number {thread_number}")

			files = getFiles(url, request.text)
			file_dict.update(files)

		else:
			continue
	return valid_subdomains, file_dict




def getFiles(url, html):

	"""
	Scrapes the html for possible files that are being linked to in the html and stores them in a dictionary
	of key:value pairs equivalent to url:file
	:param url: str
	:param html: str
	:return file_dict: dict
	"""

	file_dict = {}
	pattern = r'href="(.+?)"'
	files = re.findall(pattern, html)
	file_dict[url] = []
	file_dict[url].append(url + file for file in files)
	logger.info(f"Found {len(files)} files for {url} on thread {current_thread().name}")
	return file_dict
