#-*- coding: utf-8 -*-

'''
date  : 2017. 04. 01
author: dato
where : SNU milab
what  : calculate similairty among data-pairs
'''

import networkx as nx
import numpy as np
import scipy as sp
import time
from random import choice
from math import log
import codecs
import csv
from scipy import stats
from sklearn.metrics.pairwise import cosine_similarity
import dato_utils


IS_CHINESE_TEST = False


if IS_CHINESE_TEST:
    G = nx.read_graphml('./data/graphs/chinese_graph.graphml', unicode) # Chinese graph
else:
    G = nx.read_graphml('./data/graphs/bipartite_graph.graphml', unicode) # Korean language graph    
    #G = nx.read_graphml('./data/graphs/bipartite_2hanja_words.graphml', unicode) # Korean language graph    

    
gen = nx.connected_component_subgraphs(G)
G = next(gen)

# create forlder for output
dato_utils.create_dir('result')
output_dir = "./result"

sts = nx.bipartite.sets(G)

words = None
hanjas = None
wordSet = None
if len(sts[0]) > 6000: 
    words = list(sts[0])
    wordSet = sts[0]
    hanjas = list(sts[1])
else: 
    words = list(sts[1])
    wordSet = sts[1]
    hanjas = list(sts[0])

    
# index = list order in words 
wordic = {G.node[e]['chinese']:k for k,e in enumerate(words)}

synonyms = None

if IS_CHINESE_TEST:
    with codecs.open('./data/synonyms/chinesetools_synonym_merge.csv', 'r', encoding='utf-8') as f:
    #with codecs.open('./data/synonyms/all_chinese_synonyms.csv', 'r', encoding='utf-8') as f:
        synonyms = [line.strip() for line in f]
        
else:
    with codecs.open('./data/synonyms/korean_synonyms.csv', 'r', encoding='utf-8') as f:
        synonyms = [line.strip() for line in f]


A = nx.bipartite.biadjacency_matrix(G, hanjas)
#A = A.asfptype()
#A = A.tolil()
A = A.astype(float)

#weight = True # In case we want to do TF-IDF weighting
weight = False # In case we chose not to do TF-IDF weighting


if weight:
    rowsums = A.sum(axis=1)
    colsums = A.sum(axis=0)
    print("Starting matrix weighting...")
    for rn in range(A.shape[0]): # Row num
        for cn in range(A.shape[1]):
            if A[rn,cn] == 0: continue
            A[rn,cn] = A[rn,cn]/colsums[0,cn] * log(A.shape[1]/rowsums[rn,0])
    print("Done weighting the matrix.")

    
minK = 1000
maxK = 3000

print("Starting")

for k in range(minK, maxK, 500):
    
    synDP = []
    randDP = []
    
    st = time.clock()

    print("Factorizing for k={}".format(k))
    U, s, V = sp.sparse.linalg.svds(A, k)
    Vtr = V.transpose()

    print("Factorized. Obtaining distribution.")

    # synonyms delimeter : ','  ex) 01,34

    no_cnt = 0
    cnt = 0
    
    # calculate similarity among synonyms pairs
    for pr in synonyms:

        word = pr.split(',')
        c1 = word[0]
        c2 = word[1]

        if c1 not in wordic or c2 not in wordic: 
            no_cnt = no_cnt + 1
            continue
            
        cnt = cnt + 1

        v1 = Vtr[wordic[c1]]
        v2 = Vtr[wordic[c2]]
        synDP.append([ np.dot(v1,v2), c1.encode('utf-8'), c2.encode('utf-8') ] )
        #synDP.append([ cosine_similarity(v1,v2)[0][0], c1.encode('utf-8'), c2.encode('utf-8') ] )
        # cosine_distance
        #synDP.append([ 1 - cosine_similarity(v1,v2)[0][0], c1.encode('utf-8'), c2.encode('utf-8') ] )

    # calculate similarity among random pairs
    #for _ in synonyms:
    for _ in xrange(cnt):
        v1 = choice(Vtr)
        v2 = choice(Vtr)
        randDP.append(np.dot(v1,v2))

        
    del U
    del s
    del V
    end = time.clock()
    
    print "complete"
    print("Saving. Took {} seconds for k={}. Worked with {} syn, {} random pairs."
          .format(end-st,k,len(synDP),len(randDP)))
    
    with codecs.open("{}/randdist_k={}.csv".format(output_dir, k), 'w', encoding='utf-8') as f:
        wr = csv.writer(f)
        wr.writerows([[r] for r in randDP])

    with codecs.open("{}/syndist_k={}.csv".format(output_dir, k), 'w') as f:
        wr = csv.writer(f)
        wr.writerows(synDP)
