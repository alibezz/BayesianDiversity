'''
Baseline: latent-factor model from 
Cremonesi, Koren, and Turrin (RecSys 2010)
'''

import numpy
import sys
from scipy import sparse
from sparsesvd import sparsesvd
from predictor import Predictor


class PureSVDPredictor(object):

    def __init__(self, i, u, num_facs):
        self.item_ratings = i
        self.user_ratings = u    
        self.num_facs = num_facs

        self.m = len(self.user_ratings.keys())
        self.n = len(self.item_ratings.keys())
        self.user_positions, self.item_positions = self.__map_IDs_to_positions()

        self.U, self.S, self.Q = self.__factorize_rating_matrix()

    def __factorize_rating_matrix(self):

        mat = sparse.lil_matrix((self.m,self.n))
        for user in self.user_ratings.keys():
            for item in self.user_ratings[user]:
                mat[self.user_positions[user], self.item_positions[item]] = self.user_ratings[user][item]

        u, s, q = sparsesvd(sparse.csc_matrix(mat), self.num_facs)

        return u.T, numpy.diag(s), q

    def __map_IDs_to_positions(self):
        '''
        user and item IDs do not coincide with matrix positions, that go from 0 to m,n respectively.
        this is why we have to create this mapping
        '''

        user_pos = 0; user_map = {}
        item_pos = 0; item_map = {}

        for user in self.user_ratings.keys():
            if not user in user_map:
                user_map[user] = user_pos
                user_pos += 1
            for item in self.user_ratings[user]:
                if not item in item_map:
                    item_map[item] = item_pos
                    item_pos += 1
        return user_map, item_map

if __name__=="__main__":

    '''
    sys.argv[1] => training data
    sys.argv[2] => test data
    sys.argv[3] => data separator
    '''
    training = Predictor(sys.argv[1], sys.argv[3])
    training_users, training_items = training.store_data_relations() #~100MB
    num_factors = 50
    recommender = PureSVDPredictor(training_items, training_users, num_factors)
