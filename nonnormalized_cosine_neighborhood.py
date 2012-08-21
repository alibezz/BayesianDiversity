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
        self.__extractSimilarItems(threshold=100)


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
        scores.sort(); scores.reverse();
        return dict((y, x) for x, y in scores[:threshold])

    def __extractSimilarItems(self, threshold=60):
        
        self.similar_items = {}

        c = 0
        for item in self.item_ratings:
            # Status updates for large datasets
            c += 1
            if c % 100 == 0: print "%d / %d" % (c,len(self.item_ratings))
            self.similar_items[item] = self.__topMatches(item,threshold)

    def get_recommendations(self, person, item_threshold=10):

        user_ratings = self.user_ratings[person]
        scores = {}

        # Loop over items rated by this user
        for (item, rating) in user_ratings.items():
            # Loop over items similar to this one
            try:
                for (similarity,item2) in self.similar_items[item][:item_threshold]:
                    if item2 in user_ratings: continue
                    scores.setdefault(item2,0.0)
                    scores[item2] += similarity * rating
            except:
                continue
                
        rankings = [(score,item) for item,score in scores.items()]
        rankings.sort(); rankings.reverse()
        return rankings   

    def get_cremonesi_ratings(self, user, selected_items):
        '''
        applies NNCosNgbr, but instead of searching items in similar_items 
        within a threshold, searches for all selected_items and generates 
        scores for all of them.
        '''
        user_ratings = []
        try:
            user_ratings = self.user_ratings[user]
        except:
            return []
        scores = {}

        # Loop over items rated by this user
        for (item, rating) in user_ratings.items():
            for item2 in selected_items:
                scores.setdefault(item2,0)
                if item2 in self.similar_items[item]:
                    scores[item2] += self.similar_items[item][item2] * rating
        rankings = [(score,item) for item,score in scores.items()]
        rankings.sort(); rankings.reverse()
        return rankings   

    def choose_some_items(self, item_ids, user_items, target_item, K):
        '''
        Selects K items in the dataset (item_ids) randomly, 
        excluding those that were rated by a certain user (user_items)
        and appending the target_item
        '''
        items = list(set(item_ids) - set(user_items))
        items.append(target_item)

        from random import sample
        return sample(items, K)

if __name__=="__main__":
    '''
    sys.argv[1] => training data
    sys.argv[2] => test data
    sys.argv[3] => data separator
    '''
    training = Predictor(sys.argv[1], sys.argv[3])
    training_users, training_items = training.store_data_relations() #~100MB
    recommender = NNCossNgbrPredictor(training_items, training_users) 

    N = 20
    ranker = Ranker(N)
    testing = Predictor(sys.argv[2], sys.argv[3])
    test_users, test_items = testing.store_data_relations()
    ev = Evaluator(test_users, N)

    item_ids = list(set(training_items.keys() + test_items.keys())) #all unique items in the dataset
    hits = 0
    div_metric1 = []
    div_metric2 = []
    for u in test_users.keys():
        for i in test_users[u].keys():

            user_items = []
            if u in training_users:
                user_items = training_users[u].keys()
            if u in test_users:
                user_items += test_users[u].keys()

            items_for_cremonesi_validation = recommender.choose_some_items(item_ids, user_items, i, 100)            
            ratings = recommender.get_cremonesi_ratings(u, items_for_cremonesi_validation)

            #recommendations = ranker.topRatings(ratings)
            recommendations = ranker.maximizeKGreatItems(1, ratings, training_items)
            hits += ev.hadAHit(recommendations, i)
            div_metric1.append(ev.simpleDiversity(recommendations, training_items))
            div_metric2.append(ev.diversityEILD(recommendations, training_items))

    test_size = 301.0
    print 'rec', hits/test_size, 'prec', hits/(test_size * N)
    print 'sim simple', sum(div_metric1)/len(div_metric1)
    print 'div vargas', sum(div_metric2)/len(div_metric2)

    #recommended_ratings = []
    # #hits = 0
    # count = 0
    # div_metric1 = []
    # div_metric2 = []
    # hits = 0.0
    # for u in users.keys():
    #     items_for_cremonesi_validation = self.choose_some_items(users[u].keys(), 0.25)
    #     #recommendations = ranker.topRatings(recommender.getRecommendations(u, item_threshold=40))
    #     recommendations = ranker.maximizeKGreatItems(1, recommender.getRecommendations(u, item_threshold=40), items)
    #     hits += ev.hits(u, recommendations)
    #     div_metric1.append(ev.simpleDiversity(recommendations, items))

    #     div_metric2.append(ev.diversityEILD(recommendations, items))

    #     #recommended_ratings += ev.totalOfRatings(u, ranker.topRatings(recommender.getRecommendations(u, item_threshold=40)))
    #     #recommended_ratings += ev.totalOfRatings(u, ranker.maximizeKGreatItems(1, recommender.getRecommendations(u, item_threshold=40), items))

    #     #hits += ev.hadAHit(u, ranker.topRatings(recommender.getRecommendations(u, item_threshold=40)))
    #     #hits += ev.hadAHit(u, ranker.maximizeKGreatItems(1, recommender.getRecommendations(u, item_threshold=40), items))
    #     count += 1
    #     if count % 100 == 0: print "%d / %d" % (count,len(users))

    # #print hits
    # #print len(recommended_ratings)
    # #print sum(recommended_ratings)/len(recommended_ratings)
    # print 'div simple', sum(div_metric1)/len(div_metric1)
    # print 'div vargas', sum(div_metric2)/len(div_metric2)
    # test_size = 301
    # print 'rec', hits/test_size, 'prec', hits/(test_size * N)
