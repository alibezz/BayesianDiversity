'''
This class contains generic 
definitions for parsing different
databases, which may be represented
by different, specialized classes
'''

import sys

#todo document variables

class ParseDatabase(object):

    def __init__(self, fname):
        self.filename = fname
        self.filelines = []
        self.f = open(self.filename, "r")
        self.instances = []

    def open_data(self):
        try:
            self.f = open(self.filename, "r")
        except IOError:
            pass

    def read_lines(self):
        try:
            self.filelines = self.f.readlines()
        except IOError:
            sys.stderr.write("Could not read datafile.")

    def close_data(self):
        try:
            self.f.close()
        except IOError:
            pass

