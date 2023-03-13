from helpers import *
from multiprocessing import cpu_count
from concurrent.futures import ThreadPoolExecutor
import threading
import sys

# TODO: Implement logging for different HTML status codes (timeout, not found, etc..)
# TODO: Implement locking and unlocking for multithreading

if len(sys.argv) != 2:
	sys.exit("Usage: python3 main.py <domain>")

DOMAIN = sys.argv[1]


def main():
	# Initializing the lists that we will use to store the valid directories and subdomains
	valid_dirs = []
	valid_subdomains = []

	# Loading the directories and subdomains from the files
	dirs, subdomains = loadFiles()

	# Dividing the directories and subdomains into lists of equal size for multithreading
	# The iteration through the list is done in steps of max_processes, ensuring that each
	# thread gets a different set of directories/subdomains
	max_processes = cpu_count() - 2 if cpu_count() >= 4 else 1
	divided_dirs = [dirs[i::max_processes] for i in range(max_processes)]
	divided_subdomains = [subdomains[i::max_processes] for i in range(max_processes)]

	# Multithreading the crawling of the directories and subdomains
	with ThreadPoolExecutor(max_workers=max_processes) as executor:
		dir_workers = [executor.submit(crawlDirs, divided_dir) for divided_dir in divided_dirs]
		domain_workers = [executor.submit(crawlDomain, divided_subdomain) for divided_subdomain in divided_subdomains]

		# Adding the resulting lists from the function calls to the valid_dirs and valid_subdomains lists
		for worker in dir_workers:
			valid_dirs.extend(worker.result())
		for worker in domain_workers:
			valid_subdomains.extend(worker.result())


def loadFiles():
	with open("input_files/dirs_dictionary.bat", "r") as f1:
		dirs = f1.read().splitlines()

	with open("input_files/subdomains_dictionary.bat") as f2:
		subdomains = f2.read().splitlines()

	return dirs, subdomains
