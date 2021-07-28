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
import numpy as np
from model_store import ModelStore
from sklearn import datasets
from sklearn.linear_model import LogisticRegression
import os

_CANDIDATE_MODEL_STORE = ModelStore(model_store.CANDIDATE)
_PRODUCTION_MODEL_STORE = ModelStore(model_store.PRODUCTION)

import numpy as np
import csv
from sklearn.datasets.base import Bunch


def load_iris_from_csv_file(f):
    with open(f) as csv_file:
        data_file = csv.reader(csv_file)
        temp = next(data_file)
        n_samples = 150  # number of data rows, don't count header
        n_features = 4  # number of columns for features, don't count target column
        feature_names = ['setosa', 'versicolor', 'virginica']
        target_names = ['f4']  # adjust accordingly
        data = np.empty((n_samples, n_features))
        target = np.empty((n_samples,), dtype=np.int)

        for i, sample in enumerate(data_file):
            data[i] = np.asarray(sample[:-1], dtype=np.float64)
            target[i] = np.asarray(sample[-1], dtype=np.int)

    return Bunch(data=data, target=target, feature_names=feature_names, target_names=target_names)


def get_dataset(d):
    print("searching for csv files in {}".format(d))
    for root, dirs, files in os.walk(d):

        for file in files:
            if file.endswith(".csv"):
                return os.path.join(d, file)
    return None


def train_model(f):
    csv_file = get_dataset(f)
    if csv_file:
        print("found {} dataset".format(csv_file))

    iris = load_iris_from_csv_file(csv_file)

    X = iris["data"][:, 3:]  # petal width
    y = (iris["target"] == 2).astype(np.int)

    model = LogisticRegression()
    model.fit(X, y)

    version = round(time.time())

    print(f'Saving model with version {version} to candidate model store.')
    _CANDIDATE_MODEL_STORE.save_model(model, version)


def validate_model():
    model, version = _CANDIDATE_MODEL_STORE.load_latest_model()
    print(f'Validating model with version {version} to candidate model store.')
    if not isinstance(model.predict([[1]]), np.ndarray):
        raise ValueError('Invalid model')
    print(f'Deploying model with version {version} to production model store.')
    _PRODUCTION_MODEL_STORE.save_model(model, version)


if __name__ == '__main__':
    cmd = sys.argv[1]
    if cmd == 'train':
        train_model(sys.argv[2])
    elif cmd == 'validate':
        validate_model()
    else:
        raise ValueError(f"Unknown command {cmd}")
