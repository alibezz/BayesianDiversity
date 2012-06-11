'''
Generic class that takes training data
and generates the necessary structures 
for predicting items in different manners
'''

import sys

class Predictor(object):

    def __init__(self, trn_filename, sep):
        self.training_filename = trn_filename
        self.separator = sep
        self.users = {}
        self.items = {}

    def store_data_relations(self):
        #TODO should be more generic
        f = open(self.training_filename, "r")
        lines = f.readlines()
        for l in lines:
            user, item, rating, timestamp = l.split(self.separator)

            try:
                self.users[user][item] = float(rating)
            except KeyError:
                self.users[user] = {item : float(rating)}
                
            try:
                self.items[item][user] = float(rating)
            except KeyError:
                self.items[item] = {user : float(rating)} 

        f.close()
        return self.users, self.items

    #todo trusting on that, check it out better
    def compute_means(self, info):
        avgs = {}
        for i in info.keys():
            avgs[i] = 0.0
            num_j = 0
            for j in info[i].keys():                
                avgs[i] += info[i][j]
                num_j += 1
            avgs[i] /= num_j
        return avgs


    def normalize_ratings(self, info):
        '''
        info is a dict either in the form
        { item : {user : rating} } or in the
        for { user : {item : rating} }
        '''
        avgs = self.compute_means(info)
        for i in info.keys():
            for j in info[i].keys():
                info[i][j] -= avgs[i]
        return info, avgs

        
if __name__=="__main__":
    a = Predictor(sys.argv[1], sys.argv[2])
    users, items = a.store_data_relations() #~100MB
    ratings, means = a.normalize_ratings(users)
