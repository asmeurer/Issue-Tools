#!/usr/bin/env python
"""
This script check issue tracker, whether comments about GCI task are inserted.

Script work with source table, check if issue_id is present, and update column
'is_inserted'

"""

from optparse import OptionParser
import logging
import os.path
import sys

from mako.template import Template

from lib.tasks import Tasks
from lib.mentors import Mentors
from lib.utilities import ask_create_dir

default_task_list_csv = "prepared-data/task-list.csv"



parser = OptionParser()
parser.set_usage("%s [options ...] [command]")

parser.add_option("--source", type="string", dest="task_list",
    help="Source task list table [default: %default]", default=default_task_list_csv)

parser.add_option("--all", dest="check_all",
    help="Check issue tracker even when the 'is_inserted' filled [default: %default]", default=False)

parser.add_option("-v", "--verbose", action="store_true", dest="verbose",
    default=False)
parser.add_option("-d", "--debug", action="store_true", dest="debug",
    default=False)

options, args = parser.parse_args()

if options.debug:
    logging.basicConfig(level=logging.DEBUG)
#elif options.verbose:

logging.basicConfig(level=logging.INFO)


def main():

    tasks = Tasks([])
    tasks.load(options.task_list)
    if "Id" not in tasks.fieldnames:
        print "It seems that column with issues-id 'Id' is not filled."
        print "Run '1-pull_issues_id.py' firstly."
        sys.exit(1)

    for task in tasks:
        _id = task.Id
        if not _id:
            logging.warning("The task #%s has not issue_id. Skipped." % task.Key)
            continue

        val_is_inserted = None
        if task.has_key('is inserted'):
            val_is_inserted = task['is inserted']

        if ((val_is_inserted=="True") or (val_is_inserted=="False")) and not options.check_all:
            logging.debug("The information about inserting comment for the task #%s (issue %s) is present already. Skip" % (task.Key, _id))
            continue

        val_is_inserted = (False, True)[val_is_inserted=="True"]


        new_is_inserted = task.check_if_comment_is_inserted()
        if new_is_inserted==None:
            logging.warning("Can't check whether comment is inserted for the task #%s (issue %s)." % (task.Key, _id))
            continue

        task['is inserted'] = ("False", "True")[new_is_inserted]

    tasks.extend_fieldnames(['is inserted'])
    tasks.save()

main()

