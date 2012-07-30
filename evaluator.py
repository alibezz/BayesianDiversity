'''
Implementation of different 
evaluation metrics for top-n
'''

class Evaluator(object):

    def __init__(self, users):
        self.users = users

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
