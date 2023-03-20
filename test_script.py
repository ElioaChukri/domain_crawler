"""
------------------------------------------------------------------------------------------------------------------------
Author name: Elio Anthony Chukri
Last edited: March 15, 2023
Project Description: Simple Python script that makes use of multithreading to brute force directories and subdomains
------------------------------------------------------------------------------------------------------------------------
"""
import concurrent.futures
from helpers import *
from multiprocessing import cpu_count, Manager
from concurrent.futures import ThreadPoolExecutor
from password_cracker import bruteForce, checkHydra
from accessories import parseArguments, createLogger
import sys
import threading
from tqdm import tqdm

# Initializing the variables that will be shared by all thread through a Manager object
manager = Manager()
count_dir = manager.Value('i', 0)
count_domain = manager.Value('i', 0)

# Get CLI arguments
args = parseArguments()

# Remove the http/https and www from the domain entered since they are not actually part of the domain name
args.domain = args.domain.replace("http://", "").replace("https://", "").replace("www.", "")

# Create a logger object
logger = createLogger()


def main():
	# Check if the domain entered is valid
	if not validateDomain(args.domain):
		sys.exit("Invalid domain entered\n")

	# Clearing the log file
	with open("output.log", "w") as f:
		f.write("")

	# Initializing the lists that we will use to store the valid directories, subdomains, and files
	logger.info("Program started for domain: " + args.domain)
	valid_dirs = []
	valid_subdomains = []
	post_dirs = []

	# Loading the directories and subdomains from the files
	dirs, subdomains = loadFiles()
	logger.debug("Loaded directories and subdomains from input_files")

	"""
	Dividing the directories and subdomains into lists of equal size for multithreading
	The iteration through the list is done in steps of max_processes, ensuring that each
	thread gets a different set of directories/subdomains
	"""

	# Checking if number of threads requested is greater than number present on the system
	if args.threads > cpu_count():
		threads = cpu_count()
		logger.debug("Number of threads entered is greater than the number of cores on your system, using " + str(
			threads) + " threads instead")

	max_processes = args.threads
	logger.debug("Using " + str(max_processes) + " threads")
	divided_dirs = [dirs[i::max_processes] for i in range(max_processes)]
	divided_subdomains = [subdomains[i::max_processes] for i in range(max_processes)]

	logger.info("Divided subdomains into " + str(len(divided_subdomains)) +
	            f" lists of approx size " + str(len(subdomains) // max_processes) +
	            ", total length: " + str(len(subdomains)))
	logger.info("Divided directories into " + str(len(divided_dirs)) +
	            " lists of approx size " + str(len(dirs) // max_processes) +
	            ", total length: " + str(len(dirs)))

	"""
	Using the ThreadPoolExecutor to create a pool of threads that will run the crawlDirs and crawlDomain functions
	and using list comprehension to run each thread on a different set of directories/subdomains
	Then after the threads are done, we add the returned values to the lists that will be used to get the files.
	The .as_completed() function ensures that the threads are done before we move on to the next step
	"""
	num_dirs = len(dirs)

	# Start threads work to crawl directories, return them, and append them to the list
	with tqdm(total=num_dirs, desc="Crawling dirs", unit="dirs", dynamic_ncols=True, smoothing=0.1) \
			as progress_bar, \
			ThreadPoolExecutor(max_workers=max_processes) as executor:
		lock = threading.Lock()
		logger.info("Crawling dirs")
		dir_workers = [
			executor.submit(crawlDirs, divided_dir, progress_bar, lock) for divided_dir in divided_dirs
		]
		for worker in concurrent.futures.as_completed(dir_workers):
			returned_dirs, returned_post1 = worker.result()
			valid_dirs.extend(returned_dirs)
			post_dirs.extend(returned_post1)
		logger.debug("All threads are done crawling dirs")

	num_subdomains = len(subdomains)

	# Start threads work to crawl subdomains, returns them, and append them to the list
	with tqdm(total=num_subdomains, desc="Crawling subdomains", unit="subdomains", dynamic_ncols=True, smoothing=0.1) \
			as progress_bar, \
			ThreadPoolExecutor(max_workers=max_processes) as executor:
		lock = threading.Lock()
		logger.info("Crawling subdomains")
		domain_workers = [
			executor.submit(crawlDomain, divided_subdomain, progress_bar, lock) for divided_subdomain in
			divided_subdomains
		]
		for worker in concurrent.futures.as_completed(domain_workers):
			returned_subdomains, returned_post2 = worker.result()
			valid_subdomains.extend(returned_subdomains)
			post_dirs.extend(returned_post2)
		logger.debug("All threads are done crawling subdomains")

		# Getting the files from the domain
		files = getFiles(f"https://{args.domain}")
		logger.debug("Got files from domain")

	# Writing the valid directories, subdomains, and files to their respective files
	writeFiles(valid_dirs, valid_subdomains, files)
	logger.debug("Wrote valid directories, subdomains, and files to their respective files")

	# Checking if the user specified a username or a password file
	if not args.username and not args.password_file:
		print("You did not specify a username and/or password file, exiting script...")
		sys.exit(0)

	print(
		"All processes have completed. The script will now attempt to find a POST endpoint to bruteforce\n\n"
	)

	if not checkHydra():
		print("Hydra is not installed on your system, cannot proceed with brute force. You can install Hydra"
		      " and then rerun the attack as a standalone script by typing 'python password_cracker.py'")
		sys.exit(1)

	if not args.username:
		username = input("Enter username: ")
	else:
		username = args.username

	if args.password_file:
		password_file = args.password_file
	else:
		while True:
			password_file = input("Enter password file: ")

			# Checking if the file exists
			if not checkFileExists(password_file):
				try:
					print("File does not exist, please try again or press CTRL-D to exit\n")
				except EOFError:
					print("Exiting program...")
					sys.exit(0)
				continue

			else:  # File exists
				break

	logger.info("Starting brute force")
	bruteForce(post_dirs, username, password_file)
	logger.debug("Brute force completed")
	logger.debug("Exiting program")

	print("Exiting program...")


if __name__ == "__main__":
	main()
