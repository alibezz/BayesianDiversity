'''
Different strategies for ranking/selecting 
N items from a predictions list
'''

import sys


class Ranker(object):
    
    def __init__(self, n):
        self.N = n


    def topRatings(self, predictions):
        return predictions[:self.N]

    def maximizeKGreatItems(self, K, predictions, items):
        for i in xrange(len(predictions) - 1):
            a  = list(set(items[predictions[0][1]].keys()) & set(items[predictions[i+1][1]].keys()))
            print len(items[predictions[0][1]].keys()), len(items[predictions[i+1][1]].keys())
            if len(a) > 4:
                return True
        return False
