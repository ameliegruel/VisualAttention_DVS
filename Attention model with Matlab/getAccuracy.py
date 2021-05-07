import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt 
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
from scipy.stats import rankdata

# get data path
data_path = sys.argv[1]

# load data
try :
    df = pd.read_csv(data_path, header=2, delimiter=';')
except FileNotFoundError:
    print("Error: The file "+data_path+" does not seem to exist.\nTo run the command without error, do:   python3 getAccuracy.py path_to_input_file")
    sys.exit()

labels = pd.read_csv(data_path, delimiter=';', header=None, nrows=2).T
labels.columns = ['Categories', 'Sample times']
labels = labels.iloc[1:]
labels = labels.reset_index().drop('index', axis=1)

# rearrange data
df.set_index('timestamps', inplace=True)   # already the case
df = pd.get_dummies(df, columns=['neuron tags'], prefix='neuron')

# clean data
labels.dropna(axis=0, how='all', inplace=True)

# feature extraction
def encode_by_frequency(df, labels):
    encoded_df = pd.DataFrame()
    
    # encode samples
    for i in range(labels.shape[0]-1):
        if i < labels.shape[0]-1:
            sample_spikes = df[
                (df.index > labels.loc[i, 'Sample times']).astype('bool') & 
                (df.index < labels.loc[i+1, 'Sample times']).astype('bool')]
        else:
            sample_spikes = df[
                (df.index > labels.loc[i+1, 'Sample times']).astype('bool')]
        encoded_row = pd.DataFrame(sample_spikes.sum()).T.astype(float)
        encoded_row['category'] = labels.loc[i+1, 'Categories']
        encoded_df = pd.concat([encoded_df, encoded_row])
    
    # format encoded dataset
    encoded_df = encoded_df.reset_index().drop('index', axis=1)
    encoded_df['category'] = encoded_df[['category']].astype(int)
    
    return encoded_df

def encode_by_time(df, labels):
    encoded_df = pd.DataFrame()
    
    # encode samples
    for i in range(labels.shape[0] - 1):
        if i < labels.shape[0] - 1:
            sample_spikes = df[
                (df.index > labels.loc[i, 'Sample times']).astype('bool') & 
                (df.index < labels.loc[i+1, 'Sample times']).astype('bool')]
        else:
            sample_spikes = df[
                (df.index > labels.loc[i+1, 'Sample times']).astype('bool')]
            
        times_to_spike = []
        for col in sample_spikes.columns.values:
            # if sample_spikes.loc[max_index, col] == 0:
            if len(sample_spikes) == 0:
                times_to_spike.append(-1)
            else:
                max_index = sample_spikes.loc[:, col].idxmax()
                times_to_spike.append(max_index - labels.loc[i, 'Sample times'])
        encoded_row = pd.DataFrame([times_to_spike], columns=sample_spikes.columns.values).astype(int)
        encoded_row['category'] = labels.loc[i+1, 'Categories']
        encoded_df = pd.concat([encoded_df, encoded_row])
    
    # format encoded dataset
    encoded_df = encoded_df.reset_index().drop('index', axis=1)
    encoded_df['category'] = encoded_df[['category']].astype(int)
    
    return encoded_df

def encode_by_rank(df, labels):
    encoded_df = pd.DataFrame()
    
    # encode samples
    for i in range(labels.shape[0] - 1):
        if i < labels.shape[0] - 1:
            sample_spikes = df[
                (df.index > labels.loc[i, 'Sample times']).astype('bool') & 
                (df.index < labels.loc[i+1, 'Sample times']).astype('bool')]
        else:
            sample_spikes = df[
                (df.index > labels.loc[i+1, 'Sample times']).astype('bool')]
        times_to_spike = []
        for col in sample_spikes.columns.values:
            # if sample_spikes.loc[max_index, col] == 0:
            if len(sample_spikes) == 0:
                times_to_spike.append(-1)
            else:
                max_index = sample_spikes.loc[:, col].idxmax()
                times_to_spike.append(max_index - labels.loc[i, 'Sample times'])
        times_to_spike = np.array(times_to_spike)
        times_to_spike[times_to_spike==-1] = np.max(times_to_spike)+1
        rank = rankdata(times_to_spike, method='min')
        
        encoded_row = pd.DataFrame([rank], columns=sample_spikes.columns.values).astype(int)
        encoded_row['category'] = labels.loc[i+1, 'Categories']
        encoded_df = pd.concat([encoded_df, encoded_row])
    
    # format encoded dataset
    encoded_df = encoded_df.reset_index().drop('index', axis=1)
    encoded_df['category'] = encoded_df[['category']].astype(int)
    
    return encoded_df

rank_encoded_df = encode_by_rank(df, labels)
time_encoded_df = encode_by_time(df, labels)
freq_encoded_df = encode_by_frequency(df, labels)


# Modeling

## Frequency coding
X = freq_encoded_df.iloc[:, :-1].values
y = freq_encoded_df.iloc[:, -1].values
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)
clf = RandomForestClassifier(random_state=42)
clf.fit(X_train, y_train)
y_pred = clf.predict(X_test)
print("Accuracy - Rate coding", end="\t\t")
print(accuracy_score(y_test, y_pred))
# print(classification_report(y_test, y_pred))

## Rank order coding
X = rank_encoded_df.iloc[:, :-1].values
y = rank_encoded_df.iloc[:, -1].values
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)
clf = RandomForestClassifier(random_state=42)
clf.fit(X_train, y_train)
y_pred = clf.predict(X_test)
print("Accuracy - Rank order coding", end="\t")
print(accuracy_score(y_test, y_pred))
# print(classification_report(y_test, y_pred))

## Latency coding
X = time_encoded_df.iloc[:, :-1].values
y = time_encoded_df.iloc[:, -1].values
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)
clf = RandomForestClassifier(random_state=42)
clf.fit(X_train, y_train)
y_pred = clf.predict(X_test)
print("Accuracy - Latency coding", end="\t")
print(accuracy_score(y_test, y_pred))
# print(classification_report(y_test, y_pred))