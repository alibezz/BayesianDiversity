'''
Parses a database from MovieLens.
'''

from parse_database import ParseDatabase
import sys
import time

class MovielensParseDatabase(ParseDatabase):

    def __init__(self, fname):
        super(MovielensParseDatabase, self).__init__(fname)
        

    def print_lines(self):
        print self.filelines

    def extract_data_from_lines(self, separator):
        for l in self.filelines: 
            self.instances.append(l.strip().split(separator))

        return self.instances

if __name__=="__main__":
    '''
    sys.argv[1]: ratings from movielens
    sys.argv[2]: separator for fields in each line
    '''
    m = MovielensParseDatabase(sys.argv[1])
    m.read_lines()
    insts = m.extract_data_from_lines(sys.argv[2]) #~400MB



#aparentemente, vou precisar de duas estruturas:
#uma que vai servir pro preditor e outra que vai
#servir pra likelihood.
#as duas so fazem uso das linhas escolhidas como
#treinamento.

#para as linhas de teste, temos que ter a lista de
#filmes por usuario com as respectivas notas

#essa classe vai fazer o seguinte: parseia as linhas 
#e as deixa disponiveis.

#uma classe pra cross validation vai pegar esses 
#dados e gerar os folds de treino e teste, guardar
#em arquivos e, possivelmente, comprimir.


