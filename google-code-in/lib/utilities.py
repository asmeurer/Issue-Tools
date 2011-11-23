
import csv, codecs, cStringIO
import os
import os.path
import logging

# CSV unicode maintenance


class UTF8Recoder:
    """
    Iterator that reads an encoded stream and re-encodes the input to UTF-8
    """
    def __init__(self, f, encoding):
        self.reader = codecs.getreader(encoding)(f)

    def __iter__(self):
        return self

    def next(self):
        return self.reader.next().encode("utf-8")


class UnicodeDictReader(object):
    """
    A CSV reader which will iterate over lines in the CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, fieldnames=None, restkey=None, restval=None, dialect=csv.excel, encoding="utf-8", **kwds):
        f = UTF8Recoder(f, encoding)
        self.reader = csv.reader(f, dialect=dialect, **kwds)

        self._fieldnames = fieldnames   # list of keys for the dict
        self.restkey = restkey          # key to catch long rows
        self.restval = restval          # default value for short rows
        self.line_num = 0


    @property
    def fieldnames(self):
        if self._fieldnames is None:
            try:
                self._fieldnames = self.reader.next()
            except StopIteration:
                pass
        self.line_num = self.reader.line_num
        return self._fieldnames

    @fieldnames.setter
    def fieldnames(self, value):
        self._fieldnames = value

    def __iter__(self):
        return self

    def next(self):
        if self.line_num == 0:
            # Used only for its side effect.
            self.fieldnames

        row = self.reader.next()
        row = [unicode(s, "utf-8") for s in row]
        self.line_num = self.reader.line_num

        # unlike the basic reader, we prefer not to return blanks,
        # because we will typically wind up with a dict full of None
        # values
        while row == []:
            row = self.reader.next()
            row = [unicode(s, "utf-8") for s in row]
        d = dict(zip(self.fieldnames, row))
        lf = len(self.fieldnames)
        lr = len(row)
        if lf < lr:
            d[self.restkey] = row[lf:]
        elif lf > lr:
            for key in self.fieldnames[lr:]:
                d[key] = self.restval
        return d


        #return [unicode(s, "utf-8") for s in row]


class UnicodeDictWriter(object):
    """
    A CSV writer which will write rows to CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, fieldnames, restval="", extrasaction="raise",
            dialect=csv.excel, encoding="utf-8", **kwds):

        self.fieldnames = fieldnames    # list of keys for the dict
        self.restval = restval          # for writing short dicts
        if extrasaction.lower() not in ("raise", "ignore"):
            raise ValueError, \
                  ("extrasaction (%s) must be 'raise' or 'ignore'" %
                   extrasaction)
        self.extrasaction = extrasaction


        # Redirect output to a queue
        self.queue = cStringIO.StringIO()
        self.writer = csv.writer(self.queue, dialect=dialect, **kwds)
        self.stream = f
        self.encoder = codecs.getincrementalencoder(encoding)()


    def _dict_to_list(self, rowdict):
        if self.extrasaction == "raise":
            wrong_fields = [k for k in rowdict if k not in self.fieldnames]
            if wrong_fields:
                raise ValueError("dict contains fields not in fieldnames: " +
                                 ", ".join(wrong_fields))
        return [rowdict.get(key, self.restval) for key in self.fieldnames]

    def writerow(self, rowdict):

        row = self._dict_to_list(rowdict)
        self.writer.writerow([s.encode("utf-8") for s in row])
        # Fetch UTF-8 output from the queue ...
        data = self.queue.getvalue()
        data = data.decode("utf-8")
        # ... and reencode it into the target encoding
        data = self.encoder.encode(data)
        # write to the target stream
        self.stream.write(data)
        # empty queue
        self.queue.truncate(0)

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)


def load_config_file():
    conf_file = os.path.expanduser('~/.sympy/issue-tools.conf')

    if os.path.exists(conf_file):
        namespace = {}
        with open(conf_file) as f:
            try:
                exec f.read() in namespace
            except (SystemExit, KeyboardInterrupt):
                raise
            except:
                print "WARNING: The config file cannot be parsed."
                pass
            else:
                print "> Using %s" % conf_file
                return namespace

    return {}


def ask_create_dir(path, is_dir=True):
    if not is_dir:
        path = os.path.dirname(path)

    if not os.path.isdir(path):
        print "Output directory '%s' does not exists" % path
        a = raw_input("create it? [y]/n >")
        if a=="n":
            return False
        os.makedirs(path)
        logging.info("Directory '%s' created" % path)
    return True
