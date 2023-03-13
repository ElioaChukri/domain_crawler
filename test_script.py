"""
------------------------------------------------------------------------------------------------------------------------
Author name: Elio Anthony Chukri
Last edited: March 13, 2023
Project Description: Simple Python script that makes use of multithreading to brute force directories and subdomains
------------------------------------------------------------------------------------------------------------------------
"""

from logger import logger
from helpers import *
from multiprocessing import cpu_count
from concurrent.futures import ThreadPoolExecutor
import sys

# TODO: Implement logging for different HTML status codes (timeout, not found, etc..)

if len(sys.argv) != 2:
	sys.exit("Usage: python3 test_script.py <domain>")

DOMAIN = sys.argv[1]


def main():
	# Initializing the lists and dictionary that we will use to store the valid directories, subdomains, and files
	logger.debug("Program started")
	valid_dirs = []
	valid_subdomains = []
	file_dict = {}  # dict because each url can have multiple files

	# Loading the directories and subdomains from the files
	dirs, subdomains = loadFiles()
	logger.debug("Loaded directories and subdomains from input_files")

	# Dividing the directories and subdomains into lists of equal size for multithreading
	# The iteration through the list is done in steps of max_processes, ensuring that each
	# thread gets a different set of directories/subdomains
	max_processes = cpu_count() - 2 if cpu_count() >= 4 else 1
	logger.debug("Using " + str(max_processes) + " threads")
	divided_dirs = [dirs[i::max_processes] for i in range(max_processes)]
	logger.debug("Divided directories into " + str(len(divided_dirs)) + " lists")
	divided_subdomains = [subdomains[i::max_processes] for i in range(max_processes)]
	logger.debug("Divided subdomains into " + str(len(divided_subdomains)) + " lists")

	# Using the ThreadPoolExecutor to create a pool of threads that will run the crawlDirs and crawlDomain functions
	# and using list comprehension to run each thread on a different set of directories/subdomains
	with ThreadPoolExecutor(max_workers=max_processes) as executor:
		dir_workers = [executor.submit(crawlDirs, divided_dir) for divided_dir in divided_dirs]
		domain_workers = [executor.submit(crawlDomain, divided_subdomain) for divided_subdomain in divided_subdomains]

		# Adding the resulting lists and dicts from the function calls to the valid_dirs
		# and valid_subdomains lists and the file_dict dict
		for worker in dir_workers:
			valid_dirs.extend(worker.result())
			logger.debug("Added valid directories to main list")

		for worker in domain_workers:
			valid_subdomains, file_dict = worker.result()
			valid_subdomains.extend(valid_subdomains)
			logger.debug("Added valid subdomains to main list")
			file_dict.update(file_dict)
			logger.debug("Added files to main dict")

	# Writing the valid directories, subdomains, and files to their respective files
	writeFiles(valid_dirs, valid_subdomains, file_dict)


if __name__ == "__main__":
	main()
