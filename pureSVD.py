'''
Baseline: latent-factor model from 
Cremonesi, Koren, and Turrin (RecSys 2010)
'''

import numpy
import sys
from scipy import sparse
from sparsesvd import sparsesvd
from predictor import Predictor
from ranker import Ranker
from evaluator import Evaluator

class PureSVDPredictor(object):

    def __init__(self, i, u, num_facs):
        self.item_ratings = i
        self.user_ratings = u    
        self.num_facs = num_facs

        self.m = len(self.user_ratings)
        self.n = len(self.item_ratings)
        self.user_positions, self.item_positions = self.__map_IDs_to_positions()

        self.U, self.S, self.Q = self.__factorize_rating_matrix()
        self.R = numpy.dot(self.U, numpy.dot(self.S, self.Q.T))
        print len(self.R), len(self.R[0])

    def __factorize_rating_matrix(self):

        mat = sparse.lil_matrix((self.m, self.n))
        for user in self.user_ratings.iterkeys():
            for item in self.user_ratings[user]:
                mat[self.user_positions[user], self.item_positions[item]] = self.user_ratings[user][item]

        u, s, q = sparsesvd(sparse.csc_matrix(mat), self.num_facs)

        return u.T, numpy.diag(s), q.T

    def __map_IDs_to_positions(self):
        '''
        user and item IDs do not coincide with matrix positions, that go from 0 to m,n respectively.
        this is why we have to create this mapping
        '''

        user_pos = 0; user_map = {}
        item_pos = 0; item_map = {}

        for user in self.user_ratings.iterkeys():
            if not user in user_map:
                user_map[user] = user_pos
                user_pos += 1
            for item in self.user_ratings[user]:
                if not item in item_map:
                    item_map[item] = item_pos
                    item_pos += 1
        return user_map, item_map

    def __get_score(self, user, item):
        '''
        given a user and an item, computes a score
        for recommendation applying pureSVD
        '''
        
        ru = self.R[self.user_positions[user]]
        qi = self.Q[self.item_positions[item]]

        return numpy.dot(ru, numpy.dot(self.Q, qi))

    def get_ratings(self, user, selected_items):
        '''
        applies pureSVD for user and selected_items,
        accumulating 'ratings' (scores, actually)
        '''

        scores = []
        for item in selected_items:
            scores.append((self.__get_score(user, item), item))

        scores.sort(); scores.reverse()
        return scores   


if __name__=="__main__":

    '''
    sys.argv[1] => training data
    sys.argv[2] => test data
    sys.argv[3] => data separator
    '''
    training = Predictor(sys.argv[1], sys.argv[3])
    training_users, training_items = training.store_data_relations() #~100MB
    num_factors = 10
    recommender = PureSVDPredictor(training_items, training_users, num_factors)

    #TODO remove redundancy wrt nncosngbr
    N = 20
    ranker = Ranker(N)
    testing = Predictor(sys.argv[2], sys.argv[3])
    test_users, test_items = testing.store_data_relations()
    ev = Evaluator(test_users, N)


    #TODO remove redundancy wrt nncosngbr
    item_ids = list(set(training_items.keys() + test_items.keys())) #all unique items in the dataset
    hits = 0
    div_metric1 = []
    div_metric2 = []
    recommended_ratings = []
    for u in test_users.keys():
        for i in test_users[u].keys():

            #TODO encapsulate it
            user_items = []
            if u in training_users:
                user_items = training_users[u].keys()
            if u in test_users:
                user_items += test_users[u].keys()

            items_for_cremonesi_validation = testing.choose_some_items(item_ids, user_items, i, 100)
            ratings = recommender.get_ratings(u, items_for_cremonesi_validation)

            recommendations = ranker.topRatings(ratings)
            #recommendations = ranker.maximizeKGreatItems(1, ratings, training_items)
            recommended_ratings += ev.totalOfRatings(u, recommendations)
            hits += ev.hadAHit(recommendations, i)
            div_metric1.append(ev.simpleDiversity(recommendations, training_items))
            div_metric2.append(ev.diversityEILD(recommendations, training_items))
             
    test_size = 301.0
    print 'rec', hits/test_size, 'prec', hits/(test_size * N)
    print 'sim simple', sum(div_metric1)/len(div_metric1)
    print 'div vargas', sum(div_metric2)/len(div_metric2)
