
This is preliminary scripts for inserting comments of GCI tasks.


## Requirements:

- to add comments [IssueTrackerAPIPython](http://code.google.com/p/support/wiki/IssueTrackerAPIPython),
    download http://code.google.com/p/gdata-python-client/downloads/list

- [mako templates](http://www.makotemplates.org/download.html)

## Description

- generate-wiki-task-list.py
    Generat wiki page of task list. Sources for that is placed in old file ./source-data/GCI-2011.csv and in the /source-data/issues-manual-edited.
    
- pull-issues-id.py
    For the GCI task list load and parse task pages to find apropriated issue id.
    The sources are: csv file, which must be saved in (by default ./source-data/saved_gci-task-list.csv ).
    The output: prepared-data/task-list.csv

- pull_is_inserted.py
    Parse issue tracker to obtain, is task list published in comments of issue or not.
    The input: prepared-data/task-list.csv
    The output: prepared-data/task-list.csv (updated or created)

- insert_comments.py
    Insert comments, by default run in simulated mode. (See --help)
    For this task an authorization informationis needed, which keeps in the ~./sympy/issue-tools.conf file like:
    ```
    username = "xxx"
    password = "yyy"
    project_name = "sympy"
    ```
## Usage

Normally the sequenses is:

0. Manually save full cvs file from google-melange.
1. pull-issues-id.py
2. pull_is_inserted.py
3. pull_is_inserted.py
4. pull_is_inserted.py -S


