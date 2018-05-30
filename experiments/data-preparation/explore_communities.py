import sys
import os
sys.path.append('/home/maciek/pyCharmProjects/mc-doi')
from datetime import datetime
import logging
from model.multi_contagion_models import MultiContagionDynamicThresholdModel as MCDOI
from data.data import Data
from model.results import Results
import pickle
from tqdm import tqdm
import numpy as np
import pandas as pd
from data.data import Data
from model.parameters import ContagionCorrelation, Adjacency
from copy import copy

directory = '/datasets/mcdoi/louvain/'

communities = pickle.load('louvain_communities.pickle')

user = 38346

for id, community in enumerate(communities):
    if user in set(community):
        print(id)
