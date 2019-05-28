#! /usr/bin/python3

# I am writing this program to print a list of web pages to PDF so I can push them to EInk Tablet.


# Configuration and input parsing 
from sys import argv            # Script parameters
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

# File of links
if len(argv) < 2:
    print("Please provide a file of \\n separated links")
    exit()
else:
    links_file = argv[1]

# Output directory
if len(argv) < 3:
    dirname = 'PDF_Download_' + now().format('YYYY-MM-DD_HH:mm:ss_') + str(randint(1,1000))
else:
    dirname = argv[2]

if not exists(dirname):
    mkdir(dirname)
   
print("Reading links from %s \nDownloading into %s" % (links_file, dirname))

# Read links from file
links = []
with open(links_file, 'r') as f:
    for i, line in enumerate(f):
        links.append(line.strip())

print("Links read as:")
pprint(links)

# Enter output directory
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
