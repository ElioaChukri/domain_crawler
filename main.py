from helpers import *
from multiprocessing import cpu_count
import requests
import threading
import sys

# TODO: Implement logging for different HTML status codes (timeout, not found, etc..)
# TODO: Implement locking and unlocking for multithreading

if len(sys.argv) != 2:
	sys.exit("Usage: python3 main.py <domain>")

DOMAIN = sys.argv[1]


def main():
	dirs, subdomains = loadFiles()
	max_processes = cpu_count() - 2 if cpu_count() >= 4 else 1
	threads = []
	for i in range(max_processes):
		if i % 2 == 0:
			t = threading.Thread(target=scrapeDirs, args=dirs)
		else:
			t = threading.Thread(target=scrapeDomains, args=subdomains)
		threads.append(t)
		t.start()

	for t in threads:
		t.join()


def loadFiles():
	with open("input_files/dirs_dictionary.bat", "r") as f1:
		dirs = f1.read().splitlines()

	with open("input_files/subdomains_dictionary.bat") as f2:
		subdomains = f2.read().splitlines()

	return dirs, subdomains
