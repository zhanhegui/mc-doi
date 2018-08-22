import pandas as pd
import os
import sys
sys.path.append('/home/maciek/pyCharmProjects/mc-doi')
from matplotlib import pyplot as plt
import csv
import numpy as np
import pickle
from data.data import Data
from collections import defaultdict
import functools
import itertools
import copy
from sklearn.metrics import confusion_matrix

path = '/nfs/maciej/mcdoi/louvain/louvain_55_123/history_20/time/size_604800'
history=20

start_time = 1332565200
end_time = 1335416399
duration_24h_in_sec = 60*60*24
time_grid = np.arange(start_time+duration_24h_in_sec,end_time+duration_24h_in_sec,duration_24h_in_sec)
iter_length = 86400

with open(os.path.dirname(os.path.dirname(os.path.dirname(path)))+'/edges', 'r', encoding='utf-8') as f:
    edges = pd.read_csv(f, header=None, names=[Data.user_1, Data.user_2])

user_dict = defaultdict(functools.partial(next, itertools.count()))
edges[Data.user_1] = edges[Data.user_1].map(user_dict)
edges[Data.user_2] = edges[Data.user_2].map(user_dict)

with open(os.path.dirname(os.path.dirname(os.path.dirname(path)))+'/event_log', 'r', encoding='utf-8') as f:
    whole_event_log = pd.read_csv(f, header=None, names=[Data.time_stamp, Data.user, Data.contagion])
whole_event_log.user = whole_event_log.user.map(user_dict)

with open(os.path.dirname(os.path.dirname(path))+'/data_obj.pickle', 'rb') as f:
    d=pickle.load(f)

with open(os.path.dirname(os.path.dirname(path))+'/contagion_dict.pickle', 'rb') as f:
    contagion_dict=pickle.load(f)

whole_event_log[Data.contagion_id] = whole_event_log[Data.contagion].map(contagion_dict)
whole_event_log=whole_event_log[whole_event_log[Data.contagion_id]<d.num_contagions]

indicators = []
I = np.full((d.num_users, d.num_contagions), False, dtype=bool)
for i in range(1,min(7,33-history)+1):
    for index, row in whole_event_log[whole_event_log[Data.time_stamp]<=time_grid[history-1] + i * iter_length].iterrows():
        I[row[Data.user]][row[Data.contagion_id]] = True
    indicators.append(I)
    I = copy.deepcopy(I)

results = []
for i in range(0, 7):
    with open(path + '/result_' + str(i) + '.pickle', 'rb') as result:
        results.append(pickle.load(result))


for i in range(1,min(7,33-history)+1):
    open(path + '/fscore_' + str(i - 1), 'w', encoding='utf-8').close()
    for user in range(d.num_users):
        with open(path + '/fscore_' + str(i - 1), 'a', encoding='utf-8') as file:
            score = confusion_matrix(indicators[i-1][user,:],results[i-1][user,:], labels=[0,1]).ravel()
            file.write(str(user) + ',' + str(score[0]) + ',' + str(score[1])+ ',' + str(score[2]) + ',' + str(score[3]) + '\n')