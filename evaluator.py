'''
Implementation of different 
evaluation metrics for top-n
'''

import math

class Evaluator(object):

    def __init__(self, users, N):
        self.users = users
        self.N = N
        
        #constant for recys2011-vargas diversity that is fixed
        #TODO should not be static if the size of recommendation lists change
        self.C = self.__normalizingConstantC(self.N)


    def totalOfRatings(self, user, predictions):
        try:
            test_items = self.users[user].keys()
        except:
            test_items = []

        predicted_items = [i[1] for i in predictions]

        recommended_ratings = []
        for i in predicted_items:
            if i in test_items:
                recommended_ratings.append(self.users[user][i])
        return recommended_ratings


    def hadAHit(self, user, predictions):
        try:
            test_items = self.users[user].keys()
        except:
            test_items = []

        predicted_items = [i[1] for i in predictions]

        recommended_ratings = []
        for i in predicted_items:
            if i in test_items:
                return 1

        return 0


    def __itemSimilarity(self, item1, item2, items):

        users1 = items[item1]; users2 = items[item2]
        users_that_liked_item1 = [i[0] for i in users1.items() if i[1] >= 4.0]
        users_that_liked_item2 = [i[0] for i in users2.items() if i[1] >= 4.0]        
        intersection = len(set(users_that_liked_item1) & set(users_that_liked_item2))

        return float(intersection)/(math.sqrt(len(users_that_liked_item1)) * math.sqrt(len(users_that_liked_item1)))


    def __rankingDiscount(self, position):
        return 0.85 ** position


    def __relativeRankingDiscount(self, position1, position2):
        return self.__rankingDiscount(max(1, position1 - position2))


    def __normalizingConstantC(self, N):
        discs = 0.0

        for i in xrange(N):
            discs += self.__rankingDiscount(i)
        return 1/discs          

    def __normalizingConstantCK(self, recommendations, recommended_items, target_item, C):
        '''
        summation for all x in rec - {target} of disc(x, target) * p(rel | il, u)
        '''

        #TODO doubt: if your predictor does not have a bound for scores, how can you use 
        #p(rel|il, u) as defined in recsys11-vargas eq. 13?
        #print recommendations, recommended_items, target_item

        Ck = 0.0
        pos_target = recommended_items.index(target_item)
        for i,v in enumerate(recommended_items):
            if v != target_item:
                Ck += self.__relativeRankingDiscount(i, pos_target)
        Ck = C/Ck
        return Ck


    def diversityEILD(self, recommendations, items):
        '''
        Distance-based metric without relevance-awareness
        from recsys11-vargas
        '''
        
        import itertools 
        recommended_items = [i[1] for i in recommendations]

        #TODO doubt: should I consider all permutations or combinations??
        
        perms = list(itertools.permutations(recommended_items, 2))
        metric = 0.0
        for p in perms:
            d = self.__itemSimilarity(p[0], p[1], items)
            disc_k = self.__rankingDiscount(recommended_items.index(p[0]))
            rel_disc = self.__relativeRankingDiscount(recommended_items.index(p[0]), recommended_items.index(p[1]))
            Ck = self.__normalizingConstantCK(recommendations, recommended_items, p[0], self.C)
            metric += d * disc_k * rel_disc * Ck
            
        return metric
