#!/usr/bin/env python

from optparse import OptionParser
import logging
import os.path
import sys

from mako.template import Template

from lib.tasks import Tasks
from lib.mentors import Mentors
from lib.utilities import ask_create_dir

default_task_list_csv = "source-data/saved_gci-task-list.cvs"
default_mentors = "source-data/mentors.csv"
default_issues_description_dir = "source-data/issues-manual-edited"
default_output_file = "prepared-data/task-list.cvs"




parser = OptionParser()
parser.set_usage("%s [options ...] [command]")

parser.add_option("--source", type="string", dest="task_list",
    help="Source task list table [default: %default]", default=default_task_list_csv)

parser.add_option("--mentors", type="string", dest="mentors",
    help="Mentor's link table [default: %default]", default=default_mentors)

parser.add_option("-o", "--output", type="string", dest="output_file",
    help="Resulted filename [default: %default]", default=default_output_file)

parser.add_option("--issues", type="string", dest="issues_dir",
    help="Directory with manual edited issue's description, updated for markdown [default: %default]", default=default_issues_description_dir)

parser.add_option("--recreate", action="store_true", dest="recreate",
    default=False, help="Do not update existing file. Recreated it")


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

    if options.recreate and os.path.exists(options.output_file):
        a = raw_input("Are you sure to delete '%s' file? : yes/[no] >" % options.output_file)
        if a <> "yes":
            options.recreate = False
    
    if not ask_create_dir(options.output_file, False):
        sys.exit()

    mentors_data = Mentors()
    mentors_data.load(options.mentors)

    source_tasks = Tasks([], mentors_data=mentors_data, issues_dir = options.issues_dir)
    source_tasks.load(options.task_list)

    if os.path.exists(options.output_file) and not options.recreate:
        update_tasks = Tasks()
        update_tasks.load(options.output_file)
        update_tasks.update(source_tasks)
    else:
        update_tasks = source_tasks

    for task in update_tasks:
        _id = None
        try:
            _id = task.Id
        except:
            pass
        if not _id:
            _id = task.serach_issue_id()
            if _id:
                task["Id"] = _id

    update_tasks.extend_fieldnames(['Id'])
    update_tasks.save(options.output_file)

main()

