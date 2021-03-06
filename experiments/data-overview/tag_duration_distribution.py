import sys
import pandas as pd
from matplotlib import pyplot as plt
import os

directory = '/nfs/maciej/mcdoi/louvain/'

sets_to_proceed_file = list(sys.argv)[1]
with open(sets_to_proceed_file, 'r', encoding='utf-8') as sets_to_proceed:
    sets_to_proceed = sets_to_proceed.readlines()
sets_to_proceed = [x.strip() for x in sets_to_proceed]

from joblib import Parallel, delayed
import time
def text_progessbar(seq, total=None):
    step = 1
    tick = time.time()
    while True:
        time_diff = time.time()-tick
        avg_speed = time_diff/step
        total_str = 'of %n' % total if total else ''
        print('step', step, '%.2f' % time_diff, 'avg: %.2f iter/sec' % avg_speed, total_str)
        step += 1
        yield next(seq)
all_bar_funcs = {
    'txt': lambda args: lambda x: text_progessbar(x, **args),
    'None': lambda args: iter,
}
def ParallelExecutor(use_bar='tqdm', **joblib_args):
    def aprun(bar=use_bar, **tq_args):
        def tmp(op_iter):
            if str(bar) in all_bar_funcs.keys():
                bar_func = all_bar_funcs[str(bar)](tq_args)
            else:
                raise ValueError("Value %s not supported as bar type"%bar)
            return Parallel(**joblib_args)(bar_func(op_iter))
        return tmp
    return aprun

aprun = ParallelExecutor(n_jobs=16)

ready_hists = set()
for root, dirs, files in os.walk('/nfs/maciej/mcdoi/louvain/data-overview/', topdown=False):
    for name in files:
        ready_hists.add(os.path.join(root, name))

def tag_dist_for_set(set, ready):
    num_users = set.split('/')[5].split('_')[2]
    set_id = set.split('/')[5].split('_')[1]
    for i in range(1,34):
        diff = []
        if directory+'data-overview/'+num_users+'_'+set_id+'_hist_'+str(i)+'_duration_dist.png' not in ready:
            if sum(1 for line in open(set + '/history_' + str(i) + '/event_log', 'r', encoding='utf-8')) > 0:
                event_log = pd.read_csv(set + '/history_' + str(i) + '/event_log', header=None)
                event_log.columns = ['ts', 'user', 'contagion']
                tags_list = event_log['contagion'].unique()
                for tag in tags_list:
                    d = event_log[event_log['contagion']==tag]['ts'].max()-event_log[event_log['contagion']==tag]['ts'].min()
                    if d>0:
                        diff.append(d)
                plt.figure()
                plt.hist(diff, bins=50)
                plt.title('Num of tags: '+ str(len(tags_list)) +', history ' + str(i))
                plt.xlabel('Tag duration (last-first)')
                plt.savefig(directory+'data-overview/'+num_users+'_'+set_id+'_hist_'+str(i)+'_duration_dist.png', dpi=72)
                plt.close('all')

if __name__ == '__main__':
    aprun(bar='txt')(delayed(tag_dist_for_set)(set,ready_hists) for set in sets_to_proceed)