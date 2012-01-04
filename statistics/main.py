#!/usr/bin/env python
from __future__ import division
from threading import Thread
from math import floor
from time import sleep
from argparse import ArgumentParser
import re
import os
import gdata.projecthosting.client
import gdata.projecthosting.data
import gdata.client
import gdata.data
import atom.http_core
import atom.core

helpText = "Google Code Issue Tracker (developed for Sympy)"
maxIssues = 1000000
iter = 1000
numThreads = 20
issuesPerThread = 25

def percent_graphs(label, titles, data, length=57, graph_fill="#"):
    s = label + "\n"
    for tag in titles:
        frequency = data.count(tag)/len(data)
        tag += ":"
        bars = ""
        for i in range(int(length*frequency)):
            bars += graph_fill
        percent = floor(frequency*1000)/10
        s += "{tag:<15}[{bars:<57}]{percent: >5}%\n".format(tag=tag, bars=bars, percent=percent)
    s += "\n"
    return s

class Issue:
    def __init__(self, id, title, stars, status, comments=None):
        self.id = id
        self.title = title
        self.stars = stars
        self.status = status
        self.comments = comments

class Tag:
    def __init__(self, tag, count):
        self.tag = tag
        self.count = count

class CommentGetter(Thread):
    def __init__(self, issues_list, id):
        Thread.__init__(self, None, None, "CommentGetter" + `id`)
        self.list = issues_list
    def run(self):
        for issue in self.list:
            cquery = gdata.projecthosting.client.Query(start_index=1, max_results=500)
            issue.comments = gdata_client.get_comments(PROJECTNAME, issue.id, query=cquery)

parser = ArgumentParser(description=helpText)
parser.add_argument("-f", "--filter", action="store", default="all", choices=("all", "open", "closed"), help="Specifies a state filter for issue processing")
parser.add_argument("-s", "--sortby", action="store", default="stars", choices=("stars", "comments", "id"), help="Specifies a sorting method for issue processing")
parser.add_argument("-p", "--projectname", action="store", default="sympy", help="Google Code Project name")
options = parser.parse_args()
PROJECTNAME = options.projectname
gdata_client = gdata.projecthosting.client.ProjectHostingClient()
issues_list = []
priority_tags = ["Critical", "High", "Medium", "Low"]
type_tags = ["Defect", "Enhancement", "Other"]
status_tags = ["New", "Accepted", "Started", "NeedsDecision", "Fixed", "Verified", "Invalid", "Duplicate", "WontFix"]
states = ["open", "closed"]
comments_categories = ["0", "1-5", "6-10", "11-15", "16-20", "21-25", "26-30", ">30"]
comments_bounds = [1, 6, 11, 15, 21, 26, 31, 100000000]
other_tags = []
ptags_list = []
type_tags_all = []
status_tags_all = []
other_tags_all = []
other_tags_list = []
states_values = []
comments_values = []
for i in range(1, maxIssues, iter):
    print "Obtaining issues " + `i` + " through " + `i + iter - 1`
    gdata_query = gdata.projecthosting.client.Query(start_index=i, max_results=iter)
    all_issues_raw = gdata_client.get_issues(PROJECTNAME, query=gdata_query)
    if len(all_issues_raw.entry) == 0:
        break
    for current_issue in all_issues_raw.entry:
        if current_issue.state.text != options.filter and options.filter != "all":
            continue
        issue_id_location = re.search("[0-9]+", current_issue.id.text)
        issue_id = int(current_issue.id.text[issue_id_location.start():issue_id_location.end()])
        issue_title = current_issue.title.text
        issue_stars_location = re.search("[0-9]+", current_issue.stars.text)
        issue_stars = int(current_issue.stars.text[issue_stars_location.start():issue_stars_location.end()])
        issues_list.append(Issue(issue_id, issue_title, issue_stars, current_issue.state.text))
        states_values.append(current_issue.state.text)
        if current_issue.status:
            status_tags_all.append(current_issue.status.text)
        else:
            status_tags_all.append("")
        for tag in current_issue.label:
            if re.match("Priority-", tag.text):
                tag.text = re.sub("Priority-", "", tag.text)
                ptags_list.append(tag.text)
            elif re.match("Type-", tag.text):
                tag.text = re.sub("Type-", "", tag.text)
                type_tags_all.append(tag.text)
            else:
                if tag.text not in other_tags:
                    other_tags.append(tag.text)
                other_tags_all.append(tag.text)
print "Obtaining comments"
numIssues = len(issues_list)
curIssue = 0
numDone = 0
threads = []
for i in range(0, numThreads):
    threads.append(None)
while numDone < len(issues_list):
    for i in range(0, numThreads):
        if threads[i] != None:
            if threads[i].isAlive() == False:
                numDone += len(threads[i].list)
                for issue in threads[i].list:
                    comments = 0
                    if issue.comments != None:
                        comments = len(issue.comments.entry)
                        for j in range(0, len(comments_categories)):
                            if (comments < comments_bounds[j]):
                                comments_values.append(comments_categories[j])
                                break
                if len(threads[i].list) > 0:
                    print "{0} issues of {1} processed".format(numDone, len(issues_list))
                threads[i] = None
    for i in range(0, numThreads):
        if threads[i] == None:
            curList = []
            while len(curList) < issuesPerThread and curIssue < len(issues_list):
                curList.append(issues_list[curIssue])
                curIssue += 1
            threads[i] = CommentGetter(curList, i)
            threads[i].start()
    sleep(0.01) #Frees up processer for the CommentGetter threads
print "Processing data"
if not os.path.exists("out"):
  os.makedirs("out")
outsummary = open("out/summary.txt", "w")
outsummary.write("Google Code Issue Tracker: Project {name}\n".format(name=PROJECTNAME))
outsummary.write("Filter: {filter}\n".format(filter=options.filter))
outsummary.write("Sort method: {method}\n".format(method=options.sortby))
outsummary.write("Issues processed: {num}\n".format(num=len(issues_list)))
outsummary.close()
outgraphs = open("out/graphs.txt", "w")
outgraphs.write("Issue Graphs for project {project}\n\n".format(project=PROJECTNAME))
outgraphs.write(percent_graphs("Priority frequencies", priority_tags, ptags_list))
outgraphs.write(percent_graphs("Type frequencies", type_tags, type_tags_all))
outgraphs.write(percent_graphs("Status frequencies", status_tags, status_tags_all))
outgraphs.write(percent_graphs("State frequencies", states, states_values))
outgraphs.write(percent_graphs("Number of comments", comments_categories, comments_values))
outgraphs.close()
outissues = open("out/issues.txt", "w")
if options.sortby == "stars":
    issues_list.sort(key=lambda Issue: (Issue.stars), reverse=True)
elif options.sortby == "comments":
    issues_list.sort(key=lambda Issue: len(Issue.comments.entry), reverse=True)
elif options.sortby == "id":
    issues_list.sort(key=lambda Issue: (Issue.id), reverse=False)
outissues.write("Issue List for project {project}\n".format(project=PROJECTNAME))
outissues.write("Sort method: {method}\n".format(method=options.sortby))
outissues.write("{indexlabel:<6}{idlabel:<6}{namelabel:<50}{starlabel:<6}{commentslabel:<9}{statuslabel:<7}\n".format(indexlabel="Index", idlabel="ID", namelabel="Issue Title", starlabel="Stars", commentslabel="Comments", statuslabel="Status"))
for i in range(0, len(issues_list)):
    issue = issues_list[i]
    outissues.write("{index:<6}{issueid:<6}{name:<50.49s}{stars:<6}{comments:<9}{status:<7}\n".format(index=i, issueid=issue.id, name=issue.title.encode("ascii", "ignore"), stars=issue.stars, comments=len(issue.comments.entry), status=issue.status))
outissues.close()
print "Done"
