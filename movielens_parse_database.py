'''
Parses a database from MovieLens.
'''

from parse_database import ParseDatabase
import sys

class MovielensParseDatabase(ParseDatabase):

    def __init__(self, fname):
        super(MovielensParseDatabase, self).__init__(fname)

    def print_lines(self):
        print self.filelines

if __name__=="__main__":
    '''
    sys.argv[1]: ratings from movielens
    sys.argv[2]: separator for fields in each line
    '''
    m = MovielensParseDatabase(sys.argv[1])
    m.read_lines()
