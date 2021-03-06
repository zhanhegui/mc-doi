import sys
import os
sys.path.append('/home/maciek/pyCharmProjects/mc-doi')
from datetime import datetime
import logging
from model.multi_contagion_models import MultiContagionDynamicLinearThresholdModel as MCDOI
from data.data import Data
from model.results import Results
import pickle
from tqdm import tqdm
import numpy as np
import pandas as pd
from data.data import Data

directory = '/nfs/maciej/mcdoi/louvain/'

start_time = 1332565200
end_time = 1335416399
duration_24h_in_sec = 60*60*24
time_grid = np.arange(start_time+duration_24h_in_sec,end_time+duration_24h_in_sec,duration_24h_in_sec)

with open(directory + 'sets_to_omit', 'r', encoding='utf-8') as sets_to_omit:
    sets_to_omit = sets_to_omit.readlines()

sets_to_omit = set([x.strip() for x in sets_to_omit])

open(directory+'histories_to_omit', 'w', encoding='utf-8').close()
for dataset in tqdm(next(os.walk(directory))[1]):
    if dataset not in sets_to_omit:
        secik = directory + dataset
        edges = pd.read_csv(secik + '/edges', header=None)
        edges.columns = ['user1','user2']
        for history in range(1,31):
            file_name = secik + '/history_' + str(history)
            if sum(1 for line in open(file_name + '/event_log', 'r', encoding='utf-8')) > 0:
                event_log = pd.read_csv(file_name + '/event_log', header=None)
                event_log.columns = ['ts', 'user', 'contagion']
                if not set(event_log['user']).issubset(edges['user1'].append(edges['user2'])):
                    with open(directory + 'histories_to_omit', 'a', encoding='utf-8') as handle:
                        handle.write(dataset + '/history_' + str(history) + '\n')
