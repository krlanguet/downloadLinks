#! /usr/bin/python3
"""Download Links.
I am writing this program to print a list of web pages to PDF so I can push them to EInk Tablet.

The program reads a list of \\n separated links from the provided input and prints them to PDF.

Usage:
    downloading_linked_pages.py [<links_file>] [--output-dir <dir_name>]
    downloading_linked_pages.py (-h | --help)
    downloading_linked_pages.py --version

Options:
    --output-dir=<dir_name>   Name of directory to put PDFs in.
    -h --help                 Show this screen.
    --version                 Show version.
"""
from docopt import docopt
arguments = docopt(__doc__, version='Download Links 0.0')

# Configuration and input parsing 
from sys import stdin, stdout   # Reading links from STDIN
from arrow import now           # Current time
from random import randint      # Random integer
from os.path import exists      # Check file existence
from os import mkdir, chdir     # Make and enter directories

# Text output
from pprint import pprint

# Url manipulation
from urllib.parse import urlparse, urljoin
from os.path import splitext    # Removing filetype extensions

# Printing
from weasyprint import HTML, CSS

# Parsing input
output_dir = arguments['--output-dir']
if not output_dir:
    dirname = 'PDF_Download_' + now().format('YYYY-MM-DD_HH:mm:ss_') + str(randint(1,1000))
else:
    dirname = output_dir
    
links = []
links_file = arguments['<links_file>']
print("Reading links from", end=" ")
if not links_file:
    # Read links from STDIN
    print("STDIN")
    print("Downloading into", dirname)
    for line in stdin:
        links.append(line.strip())
else:
    # Read links from file
    print(links_file)
    print("Downloading into", dirname)
    with open(links_file, 'r') as f:
        for line in f:
            links.append(line.strip())    
print("Links read as:")
pprint(links)

# Output directory
if not exists(dirname):
    mkdir(dirname)
chdir(dirname)

# Helper for url manipulation
def join(*argv):
    result = ''
    for s in argv:
        result += s
    return result
       
# Parse links
webpages = []
for link in links:
    u = urlparse(link)
    webpages.append({
        'url': link,
        'filename': join(
            u.netloc,
            splitext(u.path)[0],
            '.pdf'
        ).replace('/', '_')
    })

# Settings for printing
css = CSS(string='@page { size: 8.5in 11in; margin: 1in }')

# Fetch and print pages
print('Beginning print')
for webpage in webpages:
    filename = webpage['filename']
    if not exists(filename):
        print("\tPrinting", filename)
        with open(filename, 'wb') as f:
            html = HTML(webpage['url'])
            f.write(html.write_pdf(stylesheets=[css]))
    else:
        print("\tFile", filename, "already present")

exit()
