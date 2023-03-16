"""
This file contains all the helper functions used in the main script
Functions such as loading the directories and subdomains from the files, writing the results to the output_files
directory, and the functions that are used to crawl the directories and subdomains
"""

import os
import requests
from test_script import count_dir, count_domain, logger
from filter import *


def validateDomain(domain):
	"""
	Checks if the domain given is valid. It is valid if it returns a 200 status code
	Args:
		domain (str): Domain to check
	Returns:
		True if the domain is valid, False otherwise
	"""
	pattern = re.compile(r"[^a-zA-Z0-9.-]")
	if pattern.match(domain):
		return False
	request = requests.get("https://" + domain)
	if request.status_code in [200, 201, 202, 203, 204, 205, 206]:
		return True
	else:
		return False


def checkFileExists(file):
	if os.path.isfile(file):
		return True
	else:
		return False


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
	Args:
		valid_dirs (list): List of valid directories
		valid_subdomains (list): List of valid subdomains
		files (list): List of all files found
	Returns:
		None
	"""

	directory = args.output_dir
	if not os.path.exists(directory):
		os.makedirs(directory)
		logger.debug("Created directory: " + directory)

	with open(f"{directory}/valid_dirs.bat", "w") as f1:
		for folder in valid_dirs:
			f1.write(folder + "\n")
		logger.debug("Wrote valid directories to file: " + f1.name)

	with open(f"{directory}/valid_subdomains.bat", "w") as f2:
		for domain in valid_subdomains:
			f2.write(domain + "\n")
		logger.debug("Wrote valid subdomains to file: " + f2.name)

	with open(f"{directory}/files.bat", "w") as f3:
		for file in files:
			f3.write(file + "\n")
		logger.debug("Wrote all all files found to file: " + f3.name)


def crawlDirs(dirs, pbar, lock):
	"""
	Queries all the possible directories listed in the file given and returns
	a list of directories that return a 202 status code
	Args:
		dirs (list): List of directories to query
		lock (threading.Lock): Lock to prevent multiple threads from writing to the same file
		pbar (tqdm.tqdm): Progress bar to show the progress of the script
	Returns:
		valid_dirs (list): List of valid directories
	"""

	valid_dirs = []
	post_urls = []
	for directory in dirs:

		with lock:
			count_dir.value += 1
			pbar.update(1)
		if count_dir.value % 10 == 0:
			logger.debug(f"Checked {count_dir.value} directories")
		if count_dir.value % 500 == 0:
			logger.info(f"Checked {count_dir.value} directories")

		url = f"https://{args.domain}/{directory}"
		try:
			request = requests.get(url)
		except requests.exceptions.ConnectionError:
			continue
		if request.status_code in [200, 201, 202, 203, 204, 205, 206]:
			valid_dirs.append(url)
			logger.info(f"Found valid directory: {url}")
			if not "Allow" in request.headers:
				continue
			if "POST" in request.headers.get("Allow"):
				logger.debug(f"Found POST request at {url}")
				result = handlePost(url)
				if result == 0:
					post_urls.append(result)
		else:
			continue
	return valid_dirs, post_urls


def crawlDomain(subdomains, pbar, lock):
	"""
	Queries all the possible subdomains listed in the file given and returns
	a list of subdomains that return a 202 status code
	Args:
	    lock (threading.Lock): Lock to prevent multiple threads from writing to the same file
	    pbar (tqdm.tqdm): Progress bar to show the progress of the script
		subdomains (list): List of subdomains to query
	Returns:
		valid_subdomains (list): List of valid subdomains
	"""

	valid_subdomains = []
	post_urls = []
	for subdomain in subdomains:

		with lock:
			count_domain.value += 1
			pbar.update(1)
		if count_domain.value % 100 == 0:
			logger.debug(f"Checked {count_domain.value} subdomains")
		if count_domain.value % 10000 == 0:
			logger.info(f"Checked {count_domain.value} subdomains")

		url = f"https://{subdomain}.{args.domain}"
		if not checkUrl(url):
			continue
		try:
			request = requests.get(url)
		except requests.exceptions.ConnectionError:
			continue
		if request.status_code in [200, 201, 202, 203, 204, 205, 206]:
			valid_subdomains.append(url)
			logger.info(f"Found valid subdomain: {url}")
			if not "Allow" in request.headers:
				continue
			if "POST" in request.headers.get("Allow"):
				logger.debug(f"Found POST request at {url}")
				result = handlePost(url)
				if result == 0:
					post_urls.append(result)
		else:
			continue
	return valid_subdomains, post_urls


def getFiles(url):
	"""
	Scrapes the html for files that are being linked to in the html and stores them in a list
	Args:
		url (str): URL to scrape for files
	Returns:
		files (list): List of files found
	"""

	html = requests.get(url).text
	links = getLinks(html)
	files = getValidFiles(links)
	logger.debug(f"Found {len(files)} files for {url}")
	return files


def handlePost(url):
	"""
	Handles POST requests by checking if the POST request requires authentication
	Args:
		url (str): URL to check for POST request
	Returns:
		0 if POST request requires authentication
		1 if POST request does not require authentication
	"""
	request = requests.post(url)
	if request.status_code in [401, 403]:
		logger.debug(f"{url} requires authentication, proceeding with brute force")
		return 0
	else:
		logger.debug(f"{url} supports POST but does not require authentication")
		return 1
