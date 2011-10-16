# Issue Tools

These are various tools that I wrote to work with SymPy's Google Code
issues.  They should be easy to adapt to other Google Code projects
(usually you just need to change a variable name in the script).

So far this includes:

- open_random_sympy_issue.py: Does what it says.  Opens a random open
SymPy issue in your default browser.  This requires the httplib2 module
(http://code.google.com/p/httplib2).

## Getting Issue Metadata

For simple metadata, you can download the csv file from the internet. 
Google Code has a very nice syntax for selecting arbitrary boolean
expressions relating to the issue metadata.  The easiest way to work
with this is to play with
http://code.google.com/p/sympy/issues/searchtips and see how it affects
the url.  Then, change the url from
http://code.google.com/p/sympy/issues/list?q=... to
http://code.google.com/p/sympy/issues/csv?q=... (note that this is the
same thing that you get by clicking the "CSV" link at the bottom of the
issues list).

For more advanced stuff, like parsing comments or making changes, you
will have to use the Google Code Python API
(http://code.google.com/p/support/wiki/IssueTrackerAPIPython) or HTTP
API (http://code.google.com/p/support/wiki/IssueTrackerAPI).  I've had
limited luck with this.  From what I tried, the Python API only returns
the first 25 issues, which is what you get from the Atom feed.  But
probably I was doing it wrong.

## TODO

- Port all scripts to Python 3.
- Give command line options to the scripts.
- Write more cool tools! (see the Ideas for New Scripts section below)

## License

Everything here is licensed under the liberal MIT license (see the
LICENSE file).  Feel free to use the code here however you like.

## Improvements

Please fork this project and improve it.  Add new scripts, or improve
already existing ones.

## Ideas for New Scripts

- We keep pushing in pull requests but forgetting to close the issue. 
Write a script that somehow fixes this problem.  Perhaps it uses a
heuristic that checks for open issues with a pull request in a comment
and flags it if the pull request is closed.

- http://code.google.com/p/support/issues/detail?id=5446 requests the
ability to work with the number of comments as a column spec.  Until
this is implemented, it would be cool to write a little script that
shows how many comments each issue has and sorts them by that.

- Get some interesting statistics from the issues, and plot them.  For
example, plot how many issues are closed for each day and how many
issues are opened for each day.  For SymPy, you could try parsing
http://groups.google.com/group/sympy-issues for historical data.

- *Add your cool idea here*
