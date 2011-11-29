#!/usr/bin/env python
from __future__ import division
import re
from datetime import *
from math import *
from operator import *
from string import *
import gdata.projecthosting.client
import gdata.projecthosting.data
import gdata.client
import gdata.data
import atom.http_core
import atom.core
def draw_percent_graphs(titles, data, length=57, graph_fill="#"):
    for tag in titles:
        frequency = data.count(tag)/len(data)
        tag += ":"
        bars = ""
        for i in range(int(length*frequency)):
            bars += graph_fill
        percent = floor(frequency*1000)/10
        print "{tag:<15}[{bars:<57}]{percent: >5}%".format(tag=tag, bars=bars, percent=percent)
    print
class Issue:
    def __init__(self, id, title, stars):
        self.id = id
        self.title = title
        self.stars = stars
class Tag:
    def __init__(self, tag, count):
        self.tag = tag
        self.count = count
gdata_client = gdata.projecthosting.client.ProjectHostingClient()
issues_list = []
priority_tags = ["Critical", "High", "Medium", "Low"]
type_tags = ["Defect", "Enhancement", "Other"]
status_tags = ["New", "Accepted", "Started", "NeedsDecision", "Fixed", "Verified", "Invalid", "Duplicate", "WontFix"]
other_tags = []
priority_tags_all_open = []
priority_tags_all_closed =[]
type_tags_all = []
status_tags_all = []
other_tags_all = []
other_tags_list = []
open_issues = []
num_open = int(0)
for i in range(1, 1000000, 1000):
    gdata_query = gdata.projecthosting.client.Query(start_index=i, max_results=1000)
    all_issues_raw = gdata_client.get_issues("sympy", query=gdata_query)
    if len(all_issues_raw.entry) == 0:
        break
    for current_issue in all_issues_raw.entry:
        issue_id_location = re.search("[0-9]+", current_issue.id.text)
        issue_id = int(current_issue.id.text[issue_id_location.start():issue_id_location.end()])
        issue_title = current_issue.title.text
        issue_stars_location = re.search("[0-9]+", current_issue.stars.text)
        issue_stars = int(current_issue.stars.text[issue_stars_location.start():issue_stars_location.end()])
        issues_list.append(Issue(issue_id, issue_title, issue_stars))
        if current_issue.state.text == "open":
            num_open += 1
            open_issues.append(issues_list[len(issues_list) - 1].id)
        if current_issue.status:
            status_tags_all.append(current_issue.status.text)
        else:
            status_tags_all.append("")
        for tag in current_issue.label:
            if re.match("Priority-", tag.text):
                tag.text = re.sub("Priority-", "", tag.text)
                if current_issue.state.text.lower() == 'open':
                    priority_tags_all_open.append(tag.text)
                elif current_issue.state.text.lower() == 'closed':
                    priority_tags_all_closed.append(tag.text)
            elif re.match("Type-", tag.text):
                tag.text = re.sub("Type-", "", tag.text)
                type_tags_all.append(tag.text)
            else:
                if tag.text not in other_tags:
                    other_tags.append(tag.text)
                other_tags_all.append(tag.text)
print "Percent by priority-open:"
draw_percent_graphs(priority_tags, priority_tags_all_open)
print "Percent by priority-closed:"
draw_percent_graphs(priority_tags, priority_tags_all_closed)
print "Percent by type:"
draw_percent_graphs(type_tags, type_tags_all)
print "Percent by status:"
draw_percent_graphs(status_tags, status_tags_all)
print "Ranked by stars:"
issues_list.sort(key=lambda Issue: (Issue.stars), reverse=True)
for i in range(0, 10):
    print "{index:>2d}. {title} ({stars:d} stars)".format(index=(i + 1), title=issues_list[i].title, stars=issues_list[i].stars)
for tag in other_tags:
    other_tags_list.append(Tag(tag, other_tags_all.count(tag)))
print
print "Top tags:"
other_tags_list.sort(key=lambda Tag: (Tag.count), reverse=True)
for i in range(0,10):
    print "{index:>2d}. {title} ({count:d} references)".format(index=(i + 1), title=other_tags_list[i].tag, count=other_tags_list[i].count)
print
table_string = "{:<15s}{:>10d}{:>10d}"
print "{:<15s}{:>10}{:>10}".format("", "Open:", "Closed:")
print table_string.format("Count:", num_open, len(issues_list) - num_open)
