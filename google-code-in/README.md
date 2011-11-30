These are scripts for inserting comments into the issue tracker for
Google Code-In tasks.

## Requirements:

- to add comments [IssueTrackerAPIPython](http://code.google.com/p/support/wiki/IssueTrackerAPIPython),
    download http://code.google.com/p/gdata-python-client/downloads/list

- [mako templates](http://www.makotemplates.org/download.html)

## Description

- generate-wiki-task-list.py
    Generat wiki page of task list. Sources for that are placed in old file ./source-data/GCI-2011.csv and in the /source-data/issues-manual-edited.

- 1-pull_issues_id.py
    For the GCI task list load and parse task pages to find appropriate
    issue id. The sources are: csv file, which must be saved in (by
    default ./source-data/saved_gci-task-list.csv ).

    The output: prepared-data/task-list.csv

- 2-pull_is_inserted.py
    Parse issue tracker to determine if each task in the task list is
    published in the comments of the corresponding issue or not.

    The input: prepared-data/task-list.csv
    The output: prepared-data/task-list.csv (updated or created)

- 3-insert_comments.py
    Insert comments, by default run in simulated mode. (See --help)
    For this task authorization information is needed, which can be kept in the
    ~./sympy/issue-tools.conf file like:
    ```
    username = "xxx"
    password = "yyy"
    project_name = "sympy"
    ```
## Usage

Normally the sequenses is:

0. Manually save full cvs file from google-melange to source-data/saved_gci-task-list.csv.
1. pull-issues-id.py
2. pull_is_inserted.py
3. pull_is_inserted.py
4. pull_is_inserted.py -S
