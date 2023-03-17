"""
This module contains a logger object that can be used to log messages to a file and the console.
You can edit the .setLevel() method to change the level of the messages that are logged.
"""

import logging
import argparse
from multiprocessing import cpu_count


# Class to customize the help message format
class CustomHelpFormatter(argparse.HelpFormatter):
	"""
	Formats the help message to display the arguments in a more readable format
	"""

	def _format_action_invocation(self, action):
		"""
		Formats the arguments in the help message
		Args:
			action (argparse.Action): Action object containing the arguments
		Returns:
			Formatted string containing the arguments
		"""
		if not action.option_strings:
			metavar, = self._metavar_formatter(action, action.dest)(1)
			return metavar
		else:
			parts = []

			# If the Optional doesn't take a value, format is `-s, --long`
			if action.nargs == 0:
				parts.extend(action.option_strings)

			# If the Optional takes a value, format is `-s ARGS, --long ARGS`
			else:
				default = action.dest.upper()
				args_string = self._format_args(action, default)
				for option_string in action.option_strings:
					parts.append(f'{option_string} {args_string}')

			return ', '.join(parts)

	def _format_action(self, action):
		"""
		Formats the help message for each argument
		Args:
			action (argparse.Action): Action object containing the arguments
		Returns:
			formatted_help (str): Formatted string containing the help message for each argument
		"""
		help_text = self._expand_help(action)
		action_header = self._format_action_invocation(action)

		# Left-justify action header strings with padding
		action_header = action_header.ljust(self._action_max_length)

		# Create the formatted help string without a line break between the action and help text
		formatted_help = f'{action_header}  {help_text}\n'

		return formatted_help


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
		formatter_class=CustomHelpFormatter,
		add_help=False
	)

	# Help argument
	parser.add_argument("-h", "--help", action="help", help="Show this help message and exit")

	# Required argument: domain
	parser.add_argument("domain", help="Specify a domain")

	# Optional argument: output_dir
	parser.add_argument("-o", "--output_dir", help="Specify the output directory", default="output_files")

	# Optional argument: threads
	parser.add_argument("-t", "--threads",
	                    type=int, default=threads,
	                    help=f"Specify the number of threads to use, (default: {threads})")

	# Optional argument: username
	parser.add_argument("-u", "--username", help="Specify the username")

	# Optional argument: password_file
	parser.add_argument("-p", "--password_file", help="Specify the password file")

	# Store arguments inside args object and return it
	arguments = parser.parse_args()
	return arguments
