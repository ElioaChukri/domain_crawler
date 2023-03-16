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
import sys

# TODO: Add a progress bar to show the progress of the program
# TODO: Add option to specify output directory for the files
# TODO: Add CLI argument to specify whether progress bar or logs should be shown, including an option to set debug level

# Check for argument presence and set DOMAIN to the first argument given
if len(sys.argv) < 2:
	sys.exit("Usage: python3 test_script.py <domain> [-t <threads>]")
else:
	DOMAIN = sys.argv[1]

# Initializing the variables that will be shared by all thread through a Manager object
manager = Manager()
count_dir = manager.Value('i', 0)
count_domain = manager.Value('i', 0)


def main():
	# Check if the domain entered is valid
	if not validateDomain(DOMAIN):
		sys.exit("Invalid domain entered\n")

	# Clearing the log file
	with open("output.log", "w") as f:
		f.write("")

	# Initializing the lists and dictionary that we will use to store the valid directories, subdomains, and files
	logger.info("Program started for domain: " + DOMAIN)
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
	max_processes = cpu_count() - 2 if cpu_count() > 2 else 1
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
	Then after the threads are done, we add the returned values to the lists that will be used to get the files
	the .as_completed() function ensures that the threads are done before we move on to the next step
	"""

	with ThreadPoolExecutor(max_workers=max_processes) as executor:
		logger.info("Crawling dirs")
		dir_workers = [executor.submit(crawlDirs, divided_dir) for divided_dir in divided_dirs]
		for worker in concurrent.futures.as_completed(dir_workers):
			returned_dirs, returned_post1 = worker.result()
			valid_dirs.extend(returned_dirs)
			post_dirs.extend(returned_post1)
		logger.debug("All threads are done crawling dirs")

	with ThreadPoolExecutor(max_workers=max_processes) as executor:
		logger.info("Crawling subdomains")
		domain_workers = [executor.submit(crawlDomain, divided_subdomain) for divided_subdomain in divided_subdomains]
		for worker in concurrent.futures.as_completed(domain_workers):
			returned_subdomains, returned_post2 = worker.result()
			valid_subdomains.extend(returned_subdomains)
			post_dirs.extend(returned_post2)
		logger.debug("All threads are done crawling subdomains")

		# Getting the files from the domain
		files = getFiles(f"https://{DOMAIN}")
		logger.debug("Got files from domain")

	# Writing the valid directories, subdomains, and files to their respective files
	writeFiles(valid_dirs, valid_subdomains, files)
	logger.debug("Wrote valid directories, subdomains, and files to their respective files")

	print(
		"All processes have completed, you now have the option to brute force the directories and subdomains"
		" that were found to support POST request authentication. This next step requires hydra to be installed on"
		" your system. If you do not have hydra installed, you can install it through the package manager of your"
		" operating system. You can run the password cracker alone by typing in the command 'python crack.py' which"
		" will be run on the current files present in the output_files directory.\n"
	)

	# Asking the user if they want to brute force the directories and subdomains that support POST request
	while True:
		choice = input(
			"Would you like to brute force the directories and subdomains that support POST request? (y/n): ")
		if choice.lower() == "y":
			if not checkHydra():
				print("Hydra is not installed on your system, cannot proceed with brute force")
				break
			input_file = input("Enter the name of the file that contains the passwords: ")

			# Checking if the file exists
			if not checkFileExists(input_file):
				try:
					print("File does not exist, please try again or press CTRL-D to exit\n")
				except EOFError:
					print("Exiting...")
					sys.exit(0)
				continue

			logger.debug("Starting brute force")
			bruteForce(post_dirs, input_file)
			break
		elif choice.lower() == "n":
			logger.debug("User chose not to brute force")
			break
		else:
			print("Invalid choice, please try again\n")


if __name__ == "__main__":
	main()
