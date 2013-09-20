#!/usr/bin/env python
"""
Opens a random open SymPy issue from Google Code in the default web browser.

Requires the httplib2 module (http://code.google.com/p/httplib2).

TODO:
- Command line arguments for various options.
"""

import httplib2
import csv
import webbrowser
import random
from io import StringIO

PROJECTNAME =  "sympy" # Change this to use a different Google Code project
googlecode_prefix = "http://code.google.com/p/"

def get_url_content(url):
    """
    This is taken from https://github.com/arthur-debert/google-code-issues-migrator.
    """
    h = httplib2.Http(".cache")
    resp, content = h.request(url, "GET")
    return content

def get_issues(issuecsv):
    issuecsv = StringIO(issuecsv.decode('utf-8'))
    return [issue for issue in csv.DictReader(issuecsv)]

def open_issue(issue_number):
    url = googlecode_prefix + PROJECTNAME + "/issues/detail?id=" + str(issue_number)
    webbrowser.open_new(url)

if __name__ == '__main__':
    url = googlecode_prefix + PROJECTNAME + "/issues/csv"
    open_issue(random.choice(get_issues(get_url_content(url)))['ID'])
