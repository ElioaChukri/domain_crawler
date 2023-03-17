# domain_crawler

This is a simple crawler that crawls a domain and returns a list of all the links on the domain.
Makes use of the powerful requests library to make HTTP requests and implements multithreading to speed up the process.
Also includes an optional password cracker script that looks for any POST endpoint on the domain that require
authentication and performs a dictionary attack using Hydra.

***

### Basic usage

```python test_script.py <domain>```

##### Optional arguments

```
$ python test_script --help

usage: test_script.py [-h] [-o OUTPUT_DIR] [-t THREADS] [-u USERNAME] [-p PASSWORD_FILE] domain

Simple script to crawl a domain for subdomains and directories

positional arguments:
domain                Specify a domain

options:
-h, --help                                      show this help message and exit
-o OUTPUT_DIR, --output_dir OUTPUT_DIR          Specify the output directory
-t THREADS, --threads THREADS                   Specify the number of threads to use, (default: 10)
-u USERNAME, --username USERNAME                Specify the username
-p PASSWORD_FILE, --password_file PASSWORD_FILE Specify the password file
```

### Output

The program will crawl the given domain, checking for all subdomains and directories present in the input_files
directory. It will then look through the html to find a list of all files the domain links to .
At the end of the program, it will write all valid subdomains, directories, and files to the output_files directory.

***

### To install

#### Clone the repository

```git clone https://github.com/ElioaChukri/domain_crawler.git```

#### Switch to script's directory

```cd domain_crawler```

#### Install the requirements

```pip install -r requirements.txt```


***

### Password Cracker

This script also includes an optional password cracker. It will attempt to crack the password of a given POST endpoint
using a given
wordlist. It will then output the password to the terminal. The password cracker makes use of the hydra CLI tool to
accomplish this.


***

#### Usage

The password cracker is optional and can be used by adding any of the two -u or -p flags to the command line arguments.
It can also be run independently by running the password_cracker.py script.
When run independently, the password cracker will check the urls present in the output_files/valid_dirs.bat and
output_files/valid_subdomains.bat files for any password protected POST endpoints. It will then attempt to crack the 
password of the given endpoint using the given wordlist.

```python password_cracker.py -u <username> -p <password_file>```

Depends on: [hydra](https://github.com/vanhauser-thc/thc-hydra)


***

### Contribute

Give me high grade, I need scholarship :)

