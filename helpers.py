import requests
from main import DOMAIN


def scrapeDirs(dirs):
	valid_dirs = crawlDirs(dirs)


def crawlDirs(dirs):
	valid_dirs = []
	for directory in dirs:
		url = f"{DOMAIN}/{directory}"
		request = requests.get(url)
		if request.status_code == 202:
			valid_dirs.append(url)
		else:
			continue
	return valid_dirs


def scrapeDomains(subdomains):
	valid_subdomains = crawlDomain(subdomains)


def crawlDomain(subdomains):
	valid_subdomains = []
	for subdomain in subdomains:
		url = f"{subdomain}.{DOMAIN}"
		request = requests.get(url)
		if request.status_code == 202:
			valid_subdomains.append(url)
		else:
			continue
	return valid_subdomains
