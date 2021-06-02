"""Example how to use PCSA (several FM Sketches) and RRT. """

import pandas as pd
import numpy as np
from DP_PDS.sketches.pcsa import PCSA
from DP_PDS.dp.rrt import RRT
from DP_PDS.dp.rrt import GRR
import time
from DP_PDS.priv_sketch import PrivSketch
import mmh3


def evaluate_union(sketch):
    avg_values = open('avg_values_new.dat', 'w')
    avg_values.write('0 0.0\n')
    for union in range(1, 16):
        union_sum = 0.0
        for j in range(15):
            start = time.process_time()
            sketch.union(union)
            end = time.process_time()

            t = '{:5.5f}'.format(end - start)
            val = float(t)
            val = round(val*1000, 2)
            union_sum += val

            print('UNION {0} Run {1}: System time: {2}ms'.format(union, str(j), str(val)))

        average = round((union_sum/15), 2)
        avg_values.write(str(union) + ' ' + str(average) + '\n')

    avg_values.close()


def evaluate_pcsa():
    values = open('pcsa_time_new.dat', 'w')
    values.write('0 0.0\n')
    for rows in range(3000, 30001, 3000):

        print('\nNew run with '+str(rows)+' rows')

        category = 'workclass'
        data = pd.read_csv('adult_mod_encoded.csv', usecols=['caseid', category], low_memory=False, nrows=rows)

        real_frequency = dict(data[category].value_counts())
        uni = list(np.unique(data[category]))

        start = time.process_time()

        sketch = PrivSketch(epsilon=300.0, uniques=uni, dp_var=GRR, nmap=256, length=32,
                                        sketch_var=PCSA, hash_function=mmh3)

        for j in range(len(data[category])):
            sketch.count_dp(data.loc[j, 'caseid'], data.loc[j, category])
        sketch.compare(real_frequency)

        end = time.process_time()

        t = '{:5.2f}'.format(end - start)
        print('System time: {}s'.format(t))
        values.write(str(int(rows/1000)) + ' ' + t + '\n')

    values.close()


if __name__ == '__main__':

    # exemplary dataset with unique ids. Adult dataset is from https://archive.ics.uci.edu/ml/datasets/Adult
    cat_col = 'workclass'
    print('newImpl with category: '+cat_col)
    df = pd.read_csv('adult_mod_encoded.csv', usecols=['caseid', cat_col], low_memory=False)
      
    real_freq = dict(df[cat_col].value_counts())
    uniques = list(np.unique(df[cat_col]))

    start_proc = time.process_time()

    sketch_dict = {'nmap': 256, 'length': 32,'r':0.1}
    private_sketch = PrivSketch(epsilon=10.0, uniques=uniques, dp_var=RRT, sketch_dict=sketch_dict,
                                            sketch_var=PCSA, hash_function=mmh3)

    for i in range(len(df[cat_col])):
        private_sketch.count_dp(df.loc[i, 'caseid'], df.loc[i, cat_col])
    private_sketch.compare(real_freq)

    middle_proc = time.process_time()
    print('privSketch: System time: {:5.3f}s'.format(middle_proc - start_proc))

    sketchesunion = private_sketch.union(private_sketch.sketch)

    end_proc = time.process_time()
    print('UNION: System time: {:5.7f}s'.format(end_proc - middle_proc))

    # evaluate_union(private_sketch)

    # evaluate_pcsa()


