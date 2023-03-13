from helpers import *
from multiprocessing import cpu_count
from concurrent.futures import ThreadPoolExecutor
import sys

# TODO: Implement logging for different HTML status codes (timeout, not found, etc..)

if len(sys.argv) != 2:
	sys.exit("Usage: python3 main.py <domain>")

DOMAIN = sys.argv[1]


def main():
	# Initializing the lists and dictionary that we will use to store the valid directories, subdomains, and files
	valid_dirs = []
	valid_subdomains = []
	file_dict = {}

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

		# Adding the resulting lists and dicts from the function calls to the valid_dirs
		# and valid_subdomains lists and the file_dict dict
		for worker in dir_workers:
			valid_dirs.extend(worker.result())
		for worker in domain_workers:
			valid_subdomains, file_dict = worker.result()
			valid_subdomains.extend(valid_subdomains)
			file_dict.update(file_dict)

	writeFiles(valid_dirs, valid_subdomains, file_dict)


