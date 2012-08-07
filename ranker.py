'''
Different strategies for ranking/selecting 
N items from a predictions list
'''

import sys
import math

class Ranker(object):
    
    def __init__(self, n):
        self.N = n


    def topRatings(self, predictions):
        return predictions[:self.N]

    def __getCommonUsers(self, users1, users2):
        common = list(set(users1.keys()) & set(users2.keys()))

        common_ratings = {}
        for user in common:
            common_ratings[user] = [users1[user], users2[user]]

        return common_ratings

    def __probabilityOfOnlyLikingCandidate(self, common_ratings):
        '''
        if rate is 4 or 5: user liked it (1).
        if it's 3, 2 or 1: user did not like it (0).

        rating 1: related to candidate item
        rating 2: related to already chosen item
        '''
        #TODO, use user biases in grades!

        if len(common_ratings) == 0: return 0.1 #smaaaaall value TODO is it adequate? change to prior, perhaps

        liked_only_candidate = 0.0
        for user in common_ratings.keys():
            rating1, rating2 = common_ratings[user]
            if rating1 >= 4 and rating2 >= 4: #TODO probability of liking BOTH candidates, not only one!
                liked_only_candidate += 1.0

        #probability is shrunk by the ammount of considered users
        #TODO sampling is something to examine
        #return liked_only_candidate/len(common_ratings)

        shrinking_factor = 1
        prob = ((1.0 * len(common_ratings))/(1.0 * shrinking_factor + len(common_ratings))) * liked_only_candidate/len(common_ratings)

        #print liked_only_candidate/len(common_ratings)
        return liked_only_candidate/len(common_ratings)


    def __normalizePredictions(self, predictions):
        maxv = -1.0

        for (value, item) in predictions:
            if value > maxv: maxv = value

            if maxv == 0: maxv += 0.01

        normalized = []
        for (value, item) in predictions:
            normalized.append((value/maxv, item))

        return normalized

    def __chooseNextItem(self, candidates, selected, items):
        #assume independency between selected items for simplicity => avoid DATA FRAGMENTATION
        #TODO see whether this is useful and whether we can change it
        #Prob(like candidate) * Prob(did not like selected1 | liked candidate) * .... * Prob(did not like selectedX | liked candidate)

        maxprob = 0.0; chosen = -1; priori_score = 0.0

        for (value, candidate) in candidates:
            prob = math.log(value + 0.01)
            for (value2, item) in selected:
                prob += math.log(self.__probabilityOfOnlyLikingCandidate(self.__getCommonUsers(items[candidate], items[item])) + 0.01)
            prob = math.exp(prob)
            if prob > maxprob: 
                maxprob = prob
                chosen = candidate
                priori_score = value

        return chosen, maxprob, priori_score


    def maximizeKGreatItems(self, K, predictions, items):

        normalized = self.__normalizePredictions(predictions)
        selected = normalized[:K]
        candidates = normalized[K:]

        while(len(selected) < self.N):
            chosen, posteriori_score, priori_score = self.__chooseNextItem(candidates, selected, items)
            if chosen == -1: break #did not choose any item at all! selected's length got stable

            selected.append((posteriori_score, chosen))
            candidates.remove((priori_score, chosen))

        print [ID for (score, ID) in selected]
        return selected
