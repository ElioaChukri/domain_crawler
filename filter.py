import re
from test_script import DOMAIN


def checkUrl(url):
	pattern = re.compile(rf"https?://([a-zA-Z0-9-]+\.)*{DOMAIN}")
	if pattern.match(url):
		return True
	else:
		return False

