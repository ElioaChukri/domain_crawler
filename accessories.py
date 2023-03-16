"""
This module contains a logger object that can be used to log messages to a file and the console.
You can edit the .setLevel() method to change the level of the messages that are logged.
"""

import logging
import argparse
from multiprocessing import cpu_count

from test_script import args

# Create a formatter to format the log messages
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Create a logger object
logger = logging.getLogger('output')
logger.setLevel(logging.DEBUG)

# Create a stream handler that writes log messages to the console
if args.logger:
	stream_handler = logging.StreamHandler()
	stream_handler.setLevel(logging.INFO)
	stream_handler.setFormatter(formatter)
	logger.addHandler(stream_handler)

# Create a file handler that writes log messages to a file
file_handler = logging.FileHandler('output.log')
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


# Get CLI arguments
def parseArguments():
	parser = argparse.ArgumentParser(description="Simple script to crawl a domain for subdomains and directories")

	# Required argument: domain
	parser.add_argument("domain", help="Specify a domain")

	# Optional argument: threads
	parser.add_argument("-t", "--threads",
	                    type=int, default=cpu_count() - 2 if cpu_count() > 4 else 1,
	                    help="Specify the number of threads to use")

	# Optional argument: logs
	parser.add_argument("--logs", nargs="?", const="INFO", default=None,
	                    choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
	                    help="Specify whether the program should display logs "
	                         "and optionally set the logging level (default: INFO)")

	# Optional argument: username
	parser.add_argument("-u", "--username", help="Specify the username")

	# Optional argument: password_file
	parser.add_argument("-p", "--password_file", help="Specify the password file")

	# Store arguments inside args object and return it
	arguments = parser.parse_args()
	return arguments
