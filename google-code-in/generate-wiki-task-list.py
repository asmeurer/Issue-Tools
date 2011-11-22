#!/usr/bin/env python

from optparse import OptionParser
import logging

from mako.template import Template

from lib.tasks import Tasks
from lib.mentors import Mentors


default_task_list_csv = "source-data/GCI-2011.csv"
default_mentors = "source-data/mentors.csv"
default_issues_description_dir = "source-data/issues-manual-edited"
default_template = "templates/GCI-2011-task-list.mako"
default_output_file = "wiki-task-list.md"




parser = OptionParser()
parser.set_usage("%s [options ...] [command]")

parser.add_option("--source", type="string", dest="task_list",
    help="Source task list table [default: %default]", default=default_task_list_csv)

parser.add_option("--mentors", type="string", dest="mentors",
    help="Mentor's link table [default: %default]", default=default_mentors)

parser.add_option("-t", "--template", type="string", dest="template",
    help="Template for wiki page [default: %default]", default=default_template)

parser.add_option("-o", "--output", type="string", dest="output_file",
    help="Resulted filename [default: %default]", default=default_output_file)

parser.add_option("--issues", type="string", dest="issues_dir",
    help="Directory with manual edited issue's description, updated for markdown [default: %default]", default=default_issues_description_dir)

parser.add_option("-v", "--verbose", action="store_true", dest="verbose",
    default=False)
parser.add_option("-d", "--debug", action="store_true", dest="debug",
    default=False)

options, args = parser.parse_args()

if options.debug:
    logging.basicConfig(level=logging.DEBUG)
elif options.verbose:
    logging.basicConfig(level=logging.INFO)


def main():
    mentors_data = Mentors()
    mentors_data.load(options.mentors)

    tasks = Tasks([], mentors_data=mentors_data, issues_dir = options.issues_dir)
    tasks.load(options.task_list)

    categories = tasks.categories
    difficulties = tasks.difficulties

    templ = Template(filename=options.template, output_encoding='utf-8')
    output = templ.render(tasks=tasks, categories=categories, difficulties=difficulties)

    with open(options.output_file, "w") as f:
        f.write(output)
        logging.info("")
        logging.info("File '%s' is generated." % options.output_file)


main()

