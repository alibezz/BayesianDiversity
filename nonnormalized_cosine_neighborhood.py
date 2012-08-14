'''
Baseline neighborhood-based predictor from 
Cremonesi, Koren, and Turrin (RecSys 2010)
'''

from predictor import Predictor
from ranker import Ranker
from evaluator import Evaluator
import sys
import numpy as np
import math

class NNCossNgbrPredictor(object):

    def __init__(self, i, u):
        self.item_ratings = i
        self.user_ratings = u    
        self.__extractSimilarItems(threshold=30)


    def __similarity(self, item1, item2, shrinking_factor=100.0):

        ratings1 = []
        ratings2 = []

        for user in self.item_ratings[item1]:
            if user in self.item_ratings[item2]:
                ratings1.append(self.item_ratings[item1][user])
                ratings2.append(self.item_ratings[item2][user])

        if len(ratings1) == 0: return 0.0

        cosine = np.inner(ratings1,ratings2)/(math.sqrt(np.inner(ratings1, ratings1)) * math.sqrt(np.inner(ratings2, ratings2)))
        return  ((1.0 * len(ratings1))/(1.0 * shrinking_factor + len(ratings1))) * cosine       


    def __topMatches(self, item, threshold):
        scores=[(self.__similarity(item,other, shrinking_factor=100), other)
                for other in self.item_ratings.keys() if other != item]
        scores.sort(); scores.reverse()
        return scores[:threshold]

    def __extractSimilarItems(self, threshold=60):
        
        self.similar_items = {}

        c = 0
        for item in self.item_ratings:
            # Status updates for large datasets
            c += 1
            if c % 100 == 0: print "%d / %d" % (c,len(self.item_ratings))
            self.similar_items[item] = self.__topMatches(item,threshold)
            #if c == 300: break

    def getRecommendations(self, person, item_threshold=10):

        user_ratings = self.user_ratings[person]
        scores = {}

        # Loop over items rated by this user
        for (item, rating) in user_ratings.items():
            # Loop over items similar to this one
            try:
                for (similarity,item2) in self.similar_items[item][:item_threshold]:
                    if item2 in user_ratings: continue
                    scores.setdefault(item2,0)
                    scores[item2] += similarity * rating
            except:
                continue
                
        rankings = [(score,item) for item,score in scores.items()]
        rankings.sort(); rankings.reverse()
        return rankings   

if __name__=="__main__":
    '''
    sys.argv[1] => training data
    sys.argv[2] => test data
    sys.argv[3] => data separator
    '''
    pred = Predictor(sys.argv[1], sys.argv[3])
    users, items = pred.store_data_relations() #~100MB
    recommender = NNCossNgbrPredictor(items, users) 
    N = 20

    ranker = Ranker(N)
    testing = Predictor(sys.argv[2], sys.argv[3])
    test_users, test_items = testing.store_data_relations()
    ev = Evaluator(test_users, N)

    #recommended_ratings = []
    #hits = 0
    count = 0
    div_metric = []
    for u in users.keys():
        
        #recommendations = ranker.topRatings(recommender.getRecommendations(u, item_threshold=40))
        recommendations = ranker.maximizeKGreatItems(1, recommender.getRecommendations(u, item_threshold=40), items)
        div_metric.append(ev.diversityEILD(recommendations, items))

        #recommended_ratings += ev.totalOfRatings(u, ranker.topRatings(recommender.getRecommendations(u, item_threshold=40)))
        #recommended_ratings += ev.totalOfRatings(u, ranker.maximizeKGreatItems(1, recommender.getRecommendations(u, item_threshold=40), items))

        #hits += ev.hadAHit(u, ranker.topRatings(recommender.getRecommendations(u, item_threshold=40)))
        #hits += ev.hadAHit(u, ranker.maximizeKGreatItems(1, recommender.getRecommendations(u, item_threshold=40), items))
        count += 1
        if count % 100 == 0: print "%d / %d" % (count,len(users))

    #print hits
    #print len(recommended_ratings)
    #print sum(recommended_ratings)/len(recommended_ratings)
    print sum(div_metric)/len(div_metric)
