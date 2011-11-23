
import re
import logging
import os.path
import httplib
from time import sleep


from utilities import UnicodeDictReader, UnicodeDictWriter

class Tasks(object):
    """
    A helper wrapper class for task list.
    """
    def __init__(self, tasks = [], mentors_data=None, **kwargs):
        self._tasks = tasks
        self._fieldnames = []
        self._mentors_data = mentors_data
        self._issues_dir = kwargs.get("issues_dir")
        self._current_filename = None

    def __iter__(self):
        self._counter = 0 
        return self

    def next(self):
        if self._counter < len(self._tasks):
            t = self._tasks[self._counter]
            self._counter += 1
            return t
        else:
            raise StopIteration

    def load(self, filename):
        self._current_filename = filename
        self._tasks = []
        with open(filename, 'rb') as f:
            reader = UnicodeDictReader(f)
            self._fieldnames = reader.fieldnames
            for row in reader:
                self._tasks.append(Task(row, mentors_data=self._mentors_data, issues_dir=self._issues_dir))

        logging.debug("Task list is loaded from the file `%s`" % filename)
        logging.debug("Columns: `%s`" % self._fieldnames)

    def extend_fieldnames(self, fieldnames):
        for name in fieldnames:
            if name not in self._fieldnames:
                self._fieldnames.append(name)

    def save(self, filename=None):
        if filename==None:
            filename = self._current_filename
        with open(filename, 'wb') as f:
            writer = UnicodeDictWriter(f, fieldnames=self._fieldnames)

            titles = {}
            for t in self._fieldnames:
                titles[t] = t
            writer.writerow(titles)

            for task in self:
                writer.writerow(task)

        logging.debug("Task list was saved to:`%s`" % filename)

    def update(self, new_tasks, unique_id = "Key"):
        """
        Join new task list to self, by unique id.
        """
        for task in new_tasks:
            _key = task[unique_id]
            if not self.exists(_key):
                logging.info("New task  #%s is appended.", _key)

    def exists(self, key):
        """
        Check if task is exists
        """
        for task in self._tasks:
            if task.Key == key:
                return True
        return False

    @property
    def fieldnames(self):
        return self._fieldnames

    @property
    def categories(self):
        """
        Retrieve a set of possible categories from a Categories column.
        """
        s = set()
        for task in self._tasks:
            value = task.Categories
            s.update([value])
        return s

    @property
    def difficulties(self):
        """
        Retrieve a set of possible difficulties from a Difficulty column.
        """
        s = set()
        for task in self._tasks:
            value = task.Difficulty
            s.update([value])
        return s

    def by_difficulty(self, difficulty):
        """
        Return tasks list which has pointed difficulty.
        """
        res = [task for task in self._tasks if task.Difficulty == difficulty]
        return Tasks(res)

    def by_category(self, category):
        """
        Return tasks list with pointed category.
        """
        res = [task for task in self._tasks if task.Difficulty == difficulty]
        return Tasks(res)

    def by_issue_id(self, issue_id):
        """
        Return tasks list with pointed category.
        """
        res = [task for task in self._tasks if (task.Id == issue_id) and (task['is inserted']=='False')]
        return Tasks(res)



class Task(dict):
    def __init__(self, row_dict, **kwargs):
        dict.__init__(self, row_dict)
        self._mentors_data  = kwargs.get("mentors_data")
        self._issues_dir    = kwargs.get("issues_dir")
        self._description = None
        self.__initialised = True

    def __getattr__(self, title):
        if title[0] <> "_":
            title = title.replace("_", " ")
        try:
            return super(Task,self).__getitem__(title)
        except KeyError:
            raise AttributeError(title)

    @property
    def filtered_lables(self):
        lables = self.AllLabels
        a = re.split("[,\s]+", lables)
        a = [ s for s in a if not re.match("CodeIn", s)]
        return ", ".join(a)

    @property
    def description(self):
        if self._description <> None:
            return self._description
        else:
            if self._issues_dir:
                if os.path.exists(self._issues_dir):
                    i = self.Id
                    fn = os.path.join(self._issues_dir, "%s.txt" % i)
                    if os.path.exists(fn):
                        with open(fn, "r") as f:
                            _description = f.read()
                            self._description = unicode(_description, "utf-8")
                            return _description
                    else:
                        logging.warning("There is not %s.txt in the issue_dir directory" % self.Id)
                else:
                    logging.warning("issues_dir is not exists: '%s'" % self._issues_dir)
            else:
                logging.warning("issues_dir is not defined")
        self._description = u''
        return self._description

    @property
    def mentors(self):
        """
        Obtain mentors list by a string with Mentor_IDs
        """
        return self._mentors_data.by_cs_linkid_string(self.Mentor_IDs)

    def retrieve_task_page(self):
        """
        Retrieve task page from google
        """
        logging.debug("Load the task page with key: %s" % self.Key)

        server = "www.google-melange.com"
        path_format = "/gci/task/view/google/gci2011/%s"

        path = path_format % self.Key

        headers = {"Accept":"Accept: text/html, application/xml, application/xhtml+xml"}
        conn = httplib.HTTPConnection(server)
        conn.request("GET", path)
        response = conn.getresponse()

        logging.debug("Response: %s, %s" % (response.status, response.reason))
        
        results = response.read()
        conn.close()
        sleep(1)
        return results

    def serach_issue_id(self):
        import re
        re_issue =re.compile("""Please see(\s|&nbsp;)+<a href="http://code.google.com/p/sympy/issues/detail[^=]+=(?P<id1>[\d]+)">[^=]+=(?P<id2>[\d]+)</a>""", re.M)
        re_issue2 =re.compile("""Please see(\s|&nbsp;)+http://code.google.com/p/sympy/issues/detail[^=]+=(?P<id1>[\d]+)""", re.M)
        
        content = self.retrieve_task_page()
        m = re_issue.search(content)
        if m:
            assert m.group('id2') == m.group('id1')
        else:
            m = re_issue2.search(content)
        if m:
            _id = unicode(m.group('id1'))
            logging.info("For task '%s' issue id is found: %s" % (self.Key, _id))
            return _id
        else:
            logging.warning("Issue id is not found for the task #%s" % self.Key)
            return None

    def check_if_comment_is_inserted(self):
        """
        If task has issue_id (Id), check issue tracker for comments about the task id.
        """

        logging.info("Check whether comment for the task #%s (issue %s) is inserted." % (self.Key, self.Id))

        if not self.Key:
            return None
        if not self.Id:
            return None

        server = "code.google.com"
        path_format = "/p/sympy/issues/detail?id=%s"

        path = path_format % self.Id

        headers = {"Accept":"Accept: text/html, application/xml, application/xhtml+xml"}
        conn = httplib.HTTPConnection(server)
        conn.request("GET", path)
        response = conn.getresponse()

        logging.debug("Response: %s, %s" % (response.status, response.reason))
        
        results = response.read()
        conn.close()
        #s = """http://www.google-melange.com/gci/task/view/google/gci2011/(?P<id1>[\d]+)"""
        s = """http://www.google-melange.com/gci/task/view/google/gci2011/%s""" % self.Key
        re_task = re.compile(s, re.M)
        m = re_task.search(results)
        res = False
        if m:
            res = True

        
        logging.info("Checking result: %s" % res)
        sleep(1)
        return res

