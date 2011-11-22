
import re
import logging
import os.path

from utilities import UnicodeDictReader

class Tasks(object):
    """
    A helper wrapper class for task list.
    """
    def __init__(self, tasks = [], mentors_data=None, **kwargs):
        self._tasks = tasks
        self._fieldnames = []
        self._mentors_data = mentors_data
        self._issues_dir = kwargs.get("issues_dir")

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
        self._tasks = []
        with open(filename, 'rb') as f:
            reader = UnicodeDictReader(f)
            self._fieldnames = reader.fieldnames
            for row in reader:
                self._tasks.append(Task(row, mentors_data=self._mentors_data, issues_dir=self._issues_dir))

        logging.debug("Task list is loaded from the file `%s`" % filename)
        logging.debug("Columns: `%s`" % self._fieldnames)

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
