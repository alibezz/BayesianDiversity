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
        print items[predictions[0][1]].keys()
        for i in xrange(60):
            a  = list(set(items[predictions[40][1]].keys()) & set(items[predictions[i][1]].keys()))
            if len(a) > 4:
                print a
                return True
        return False
