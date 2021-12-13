#
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
import sys
import time

import model_store
import pandas as pd
import numpy as np
from model_store import ModelStore
from sklearn import datasets
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn import model_selection
import os

_CANDIDATE_MODEL_STORE = ModelStore(model_store.CANDIDATE)
_PRODUCTION_MODEL_STORE = ModelStore(model_store.PRODUCTION)

import numpy as np
import csv
import argparse


def load_iris_from_csv_file(f):
    df = pd.read_csv(f, header=0).reset_index(drop=True)
    types = {col: np.float64 for col in df.columns[:-1]}
    types['label'] = np.int32
    df = df.astype(types)
    return df


def get_dataset(d):
    print("searching for csv files in {}".format(d))
    for root, dirs, files in os.walk(d):

        for file in files:
            if file.endswith(".csv"):
                return os.path.join(d, file)
    return None


def load_and_split(input_uri):
    csv_file = get_dataset(input_uri)
    if csv_file:
        print("found {} dataset".format(csv_file))

    iris = load_iris_from_csv_file(csv_file)
    return train_test_split(iris, test_size=0.2, random_state=8)


def train_model(input_uri):
    train, test = load_and_split(input_uri)
    y = train.pop("label")
    X = train.loc[:, train.columns]

    model = LogisticRegression(max_iter=500)
    model.fit(X, y)

    scoring = 'accuracy'
    results = model_selection.cross_val_score(model, X, y, cv=5, scoring=scoring)
    print(f'Accuracy in cross validation: {results.mean()*100} % ({results.std()} std)')
    version = round(time.time())

    print(f'Saving model with version {version} to candidate model store.')
    _CANDIDATE_MODEL_STORE.save_model(model, version)


def validate_model(input_uri):
    model, version = _CANDIDATE_MODEL_STORE.load_latest_model()
    print(f'Validating model with version {version} to candidate model store.')
    if not isinstance(model.predict([[1, 1, 1, 1]]), np.ndarray):
        raise ValueError('Invalid model')
    train, test = load_and_split(input_uri)
    y = test.pop("label")
    X = test.loc[:, test.columns]
    result = model.score(X, y)
    print(f'model accuracy {result*100}')
    if result < 0.85:
        raise ValueError('model accuracy under threshold (0.85  ). Model is not promoted to production')
    print(f'Deploying model with version {version} to production model store.')
    _PRODUCTION_MODEL_STORE.save_model(model, version)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--action", choices=['train', 'validate'])
    parser.add_argument("--input_uri")
    args = parser.parse_args()
    if args.action == 'train':
        train_model(args.input_uri)
    else:
        validate_model(args.input_uri)
