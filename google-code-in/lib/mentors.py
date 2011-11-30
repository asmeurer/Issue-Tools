
import logging

from utilities import UnicodeDictReader


class Mentors(object):
    """
    A helper wrapper class for task list.
    """
    def __init__(self):
        self._mentors = []

    def __iter__(self):
        self._counter = 0 
        return self

    def next(self):
        if self._counter < len(self._mentors):
            m = self._mentors[self._counter]
            self._counter += 1
            return m
        else:
            raise StopIteration

    def load(self, filename):
        self._mentors = []
        with open(filename, 'rb') as f:
            reader = UnicodeDictReader(f)
            self._fieldnames = reader.fieldnames
            for row in reader:
                self._mentors.append(row)

        logging.debug("Mentors table is loaded from the file `%s`" % filename)
        logging.debug("Columns: `%s`" % self._fieldnames)

    def by_cs_linkid_string(self, cs_linkid_string):

        # 'linkid1, linkid2, ...' --> ['linkid1', 'linkid2', ...]
        ids = cs_linkid_string.split(",")
        ids = [s.strip() for s in ids]

        # order is as of source file
        res = [m for m in self._mentors if m['link_id'] in ids]

        return res

