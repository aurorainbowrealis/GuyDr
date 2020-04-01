import pandas as pd
import math
import numpy as np
import pygeohash as pgh
import os
import glob
import json


def unique_users(main_df):
    return main_df.index 


def split_merge(dfs):
    df = None

    if len(dfs) == 1:
        df = pd.read_csv(f'./data/{dfs[0]}').set_index('profileId')
    else:
        mid = len(dfs)//2
        x = map(split_merge, [dfs[:mid],dfs[mid:]])
        df = pd.concat(x)
        df = df.loc[~df.index.duplicated(keep='last')]
        
    return df


def get_all_profiles():
    global max_density

    archives = os.listdir('./data')
    users = []
    df = split_merge(archives)
    

    main_df = split_merge(archives)
    #print(main_df.to_dict(orient='records'))
    return main_df, {'profiles': main_df.to_dict(orient='records')}


def unique_users_count(main_df):
    return len(unique_users(main_df))


def get_all_stats(main_df):
    vet = []
    cols = ['distanceEstimated', 'hasFaceRecognition', 'isNew', 'showAge']

    for i in cols:
        res = {}
        res['title'] = i
        res['counter'] = main_df[main_df[i] == True].shape[0]
        res['percent'] = res['counter'] * 100 // main_df.shape[0]
        vet.append(res)

    return vet


def get_age_properties(main_df):
    res = {}
    res['median'] = int(main_df['age'].median())
    res['avg'] = int(main_df['age'].mean())
    res['std'] = int(main_df['age'].std())
    return res
