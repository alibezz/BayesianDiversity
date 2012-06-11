'''
Very basic, baseline predictor
from Programming Collective Intelligence (O'Reilly)
'''

from predictor import Predictor
from math import sqrt, fabs
import sys

class UserBasedPredictor(object):

    def __init__(self, p, m={}):
        #means are optional. They should
        #be passed only when preferences
        #are mean-normalized
        self.prefs = p
        self.means = m

    def __sim_pearson(self, person1, person2):
        #Gets the list of mutually rated items
        si = {}
        for item in self.prefs[person1]:
            if item in self.prefs[person2]: si[item]=1

        # Find the number of elements
        n = len(si)

        # if there are no ratings in common, return 0
        if n == 0: return 0

        # Add up all the preferences
        sum1 = sum([self.prefs[person1][it] for it in si])
        sum2 = sum([self.prefs[person2][it] for it in si])

        # Sum up the squares
        sum1Sq = sum([pow(self.prefs[person1][it],2) for it in si])
        sum2Sq = sum([pow(self.prefs[person2][it],2) for it in si])

        # Sum up the products
        pSum = sum([self.prefs[person1][it]*self.prefs[person2][it] for it in si])

        # Calculate Pearson score
        num = pSum - (sum1 * sum2 /n)
        den = sqrt(fabs((sum1Sq - pow(sum1,2)/n))*fabs((sum2Sq-pow(sum2,2)/n)))
        if den == 0: return 0

        return num/den



    def getRecommendations(self, person):
        totals={}
        simSums={}
        
        for other in self.prefs:
            # don't compare me to myself
            if other == person: continue
            sim = self.__sim_pearson(person, other)
            # ignore scores of zero or lower
            if sim <= 0: continue
            for item in self.prefs[other]:
                # only score movies I haven't seen yet
                if item not in self.prefs[person]:
                    # Similarity * Score
                    totals.setdefault(item,0)
                    totals[item] += self.prefs[other][item]*sim
                    # Sum of similarities
                    simSums.setdefault(item,0)
                    simSums[item] += sim

        # Create the normalized list
        if self.means:
            rankings = [(total/simSums[item] + self.means[person],item) for item, total in totals.items()] #todo pass 100 at most or so
        else:
            rankings = [(total/simSums[item],item) for item, total in totals.items()] #todo pass 100 at most or so
        
        # Return the sorted list
        rankings.sort()
        rankings.reverse()
        return rankings


if __name__=="__main__":
    '''
    sys.argv[1] => training data
    sys.argv[2] => data separator
    '''
    a = Predictor(sys.argv[1], sys.argv[2])
    users, items = a.store_data_relations() #~100MB
    ratings, means = a.normalize_ratings(users)
    
    #recommender = UserBasedPredictor(users) #first, without normalizing

    recommender = UserBasedPredictor(ratings, means)

    print recommender.getRecommendations('5988')


#TODO use euclidian distance
