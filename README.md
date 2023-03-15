# domain_crawler

***

This is a simple crawler that crawls a domain and returns a list of all the links on the domain.
Makes use of the powerful requests library to make HTTP requests and implements multithreading to speed up the process.

***

### Usage

```python test_script.py <domain> [-t <threads>] [-u username] [-p <password_file>]```

***

### Example

```python test_script.py google.com```  
```python test_script.py google.com -t 10```
```python test_script.py google.com -u username -p password.txt```


***

### Output

The program will crawl the given domain, checking for all subdomains and directories present in the input_files 
directory. It will then output a list of all the links found on the domain. At the end of the program, it will write all
valid subdomains, directories, and files, to the output_files directory.

***

### To install

#### Clone the repository

```git clone https://github.com/ElioaChukri/domain_crawler.git```

#### Install the requirements

```pip install -r requirements.txt```

***

## Password Cracker

This script also includes an optional password cracker. It will attempt to crack the password of a given POST endpoint using a given
wordlist. It will then output the password to the terminal. The password cracker makes use of the hydra CLI tool to accomplish this.

***

### Usage

The password cracker is optional and can be used by adding the -p flag to the command line arguments.
It can also be run independently by running the password_cracker.py script.
When run independently, the password cracker will check the urls present in the output_files directory for any password protected
POST endpoints. It will then attempt to crack the password of the given endpoint using the given wordlist.

```python password_cracker.py [-t <threads>] [-u <username>] [-p <password_file>] [-w wordlist]```

***

### Dependencies

[hydra](https://github.com/vanhauser-thc/thc-hydra)

***

### Contribute

Give me grades, I need scholarship

***
