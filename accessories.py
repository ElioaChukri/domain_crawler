"""
This module contains a logger object that can be used to log messages to a file and the console.
You can edit the .setLevel() method to change the level of the messages that are logged.
"""

import logging
import argparse
from multiprocessing import cpu_count


def createLogger():
	"""
	Creates a logger object that can be used to log messages to a file and the console
	Returns:
		logger (logging.Logger): Logger object
	"""
	# Create a formatter to format the log messages
	formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

	# Create a logger object
	logger = logging.getLogger('output')
	logger.setLevel(logging.DEBUG)

	# Create a file handler that writes log messages to a file
	file_handler = logging.FileHandler('output.log')
	file_handler.setLevel(logging.DEBUG)
	file_handler.setFormatter(formatter)
	logger.addHandler(file_handler)
	return logger


# Get CLI arguments
def parseArguments():
	"""
	Parses the arguments passed to the script
	Returns:
		arguments (argparse.Namespace): Namespace object containing the arguments

	"""
	threads = cpu_count() - 2 if cpu_count() > 4 else 1
	parser = argparse.ArgumentParser(
		description="Simple script to crawl a domain for subdomains and directories",
		formatter_class=argparse.RawTextHelpFormatter
	)

	# Required argument: domain
	parser.add_argument("domain", help="Specify a domain\n\n")

	# Optional argument: output_dir
	parser.add_argument("-o", "--output_dir", help="Specify the output directory\n\n", default="output_files")

	# Optional argument: threads
	parser.add_argument("-t", "--threads",
	                    type=int, default=threads,
	                    help=f"Specify the number of threads to use, (default: {threads})\n\n")

	# Optional argument: username
	parser.add_argument("-u", "--username", help="Specify the username\n\n")

	# Optional argument: password_file
	parser.add_argument("-p", "--password_file", help="Specify the password file\n\n")

	# Store arguments inside args object and return it
	arguments = parser.parse_args()
	return arguments
