import logging

# Create a logger object
logger = logging.getLogger('example_logger')
logger.setLevel(logging.DEBUG)

# Create a file handler that writes log messages to a file
file_handler = logging.FileHandler('example.log')
file_handler.setLevel(logging.DEBUG)

# Create a stream handler that writes log messages to the console
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.DEBUG)

# Create a formatter to format the log messages
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Set the formatter on the handlers
file_handler.setFormatter(formatter)
stream_handler.setFormatter(formatter)

# Add the handlers to the logger
logger.addHandler(file_handler)
logger.addHandler(stream_handler)
