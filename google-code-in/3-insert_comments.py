#!/usr/bin/env python
"""
This script checks the source task-list file and inserts comments only
for the tasks which have is_inserted==False.

The script reads the source table, checks if issue_id is present, and
updates the column 'is_inserted', after inserting the comment.

"""

from optparse import OptionParser
import logging
import os.path
import sys

from mako.template import Template

from lib.tasks import Tasks
from lib.mentors import Mentors
from lib.utilities import ask_create_dir, load_config_file
from lib.issuetracker import SympyIssueTracker

default_task_list_csv = "prepared-data/task-list.csv"



parser = OptionParser()
parser.set_usage("%s [options ...] [command]")

parser.add_option("--source", type="string", dest="task_list",
    help="Source task list table [default: %default]", default=default_task_list_csv)

parser.add_option("--all", dest="check_all",
    help="Check issue tracker even when 'is_inserted' is True [default: %default]", default=False)

parser.add_option("-v", "--verbose", action="store_true", dest="verbose",
    default=False)
parser.add_option("-d", "--debug", action="store_true", dest="debug",
    default=False)

parser.add_option("-S", "--simulation_off", action="store_true", dest="simulation_off",
    default=False)

options, args = parser.parse_args()

if options.debug:
    logging.basicConfig(level=logging.DEBUG)
#elif options.verbose:

logging.basicConfig(level=logging.INFO)


def main():
    config = load_config_file()
    tracker = SympyIssueTracker(config)
    tracker.login()
    il = tracker.get_issues()

    tasks = Tasks([])
    tasks.load(options.task_list)
    if "Id" not in tasks.fieldnames:
        print "It seems that the column with issues-id 'Id' is not filled."
        print "Run '1-pull_issues_id.py' first, then '2-pull_is_inserted.py' to check"
        sys.exit(1)

    for task in tasks:
        _id = task.Id
        if not _id:
            logging.warning("The task #%s has no issue_id. Skipped." % task.Key)
            continue

        val_is_inserted = None
        if task.has_key('is inserted'):
            val_is_inserted = task['is inserted']

        if (val_is_inserted=="True") and not options.check_all:
            logging.debug("The comment for the task #%s (issue %s) has appearantly been inserted already. Skip" % (task.Key, _id))
            continue

        if val_is_inserted == None:
            continue

         # check it again in web
        _is_inserted = task.check_if_comment_is_inserted()

        if _is_inserted == True:
            logging.warning("For issue #%s the comment for task %s is already added" % _id)

        if (val_is_inserted == "False") and _is_inserted == False:
            # collect tasks of this issue, where 'task.is_inserted==False':
            _new = tasks.by_issue_id(_id)
            if _new:
                message_list = []
                for t in _new:
                    message_item = """%s
http://www.google-melange.com/gci/task/view/google/gci2011/%s
""" % (t.Title, t.Key)
                    t['is inserted'] = "True"

                    message_list.append(message_item)

                message = "".join(message_list)
                print
                print "For issue %s (http://code.google.com/p/sympy/issues/detail?id=%s) this comment will be added:" % (_id, _id)
                print
                print message
                print

                # insert comment
                if options.simulation_off:
                    a = raw_input("Insert comment? y/[n] > ")
                    if a=="y":
                        tracker.add_comment(_id, message)
                        print "Added."
            else:
                logging.warning("Tasks for issue #%s are not found" % _id)

    tasks.extend_fieldnames(['is_inserted'])
    tasks.save()

main()

