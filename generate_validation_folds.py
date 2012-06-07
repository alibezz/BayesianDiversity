'''
Given a list full of examples and a number K,
generates K cross validation <training, test> 
sets
'''

import sys
import random
import time
import os
import re
from movielens_parse_database import MovielensParseDatabase

class GenerateValidationFolds(object):

    def __init__(self, exs, K):
        self.examples = exs
        self.numfolds = K


    def generate_folds(self):
        ids = [ind for ind, obj in enumerate(self.examples)]
        folds = []
        fold_length = len(self.examples)/self.numfolds

        for i in xrange(self.numfolds - 1):
            #todo check the distribution sample is assuming
            folds.append(random.sample(ids, fold_length))
            ids = list(set(ids) - set(folds[i]))

        #appends Kth fold (what remains in ids), which may be a little bigger
        folds.append(ids)
        return folds

    def __create_validation_folder(self):
        folder = "validation" + str(time.time())
        cmd = "mkdir " + folder
        os.system(cmd)
        return folder
        
    def __format_example(self, example):
        line = str(example)
        line = re.sub('[\[\]\',]', '', line)
        return line + "\n"

    def __write_folds(self, fold_ids, f, folds):
        try:
            for fold_id in fold_ids:
                for example_id in folds[fold_id]:
                    f.write(self.__format_example(self.examples[example_id]))
        except IOError:
            sys.stderr.write("Could not write fold")

    def write_cross_validation_data(self, folds):
        folder = self.__create_validation_folder()

        ids = [ind for ind, obj in enumerate(folds)]
        for ind, obj in enumerate(folds):
            #change the way you write for binary w/ compression
            f = open(folder + "/test" + str(ind), "w")
            self.__write_folds([ind], f, folds)
            f.close()
            f = open(folder + "/training" + str(ind), "w") 
            self.__write_folds(list(set(ids) - set([ind])), f, folds)
            f.close()

if __name__=="__main__":

#todo refactor this, so this main won't be here anymore
    m = MovielensParseDatabase(sys.argv[1])
    m.read_lines()
    insts = m.extract_data_from_lines(sys.argv[2]) #~400MB
    a = GenerateValidationFolds(insts, int(sys.argv[3]))
    a.write_cross_validation_data(a.generate_folds())
