
"""Google Issue Tracker API"""
import gdata.projecthosting.client
import gdata.projecthosting.data
import gdata.gauth
import gdata.client
import gdata.data
import atom.http_core
import atom.core

class SympyIssueTracker():
    def __init__(self, config):
        self.config = config
        self.project_name = config["project_name"] 

    def login(self):
        config = self.config
        if config['username'] and config['password']:
            self.client = gdata.projecthosting.client.ProjectHostingClient()
            self.client.client_login(config['username'], config['password'], source='sympy-issue-tools', service="code")

    def get_issues(self, max_results=25):
        feed = self.client.get_issues(self.project_name)
        return feed.entry

    def add_comment(self, issue_id, comment, lables=[]):
        self.client.update_issue(
            self.project_name,
            issue_id,
            comment = comment)
#            summary='New Summary',
#            status='Accepted',
#            owner=assignee,
#            labels=['-label0', 'label1'],
#            ccs=[owner],

