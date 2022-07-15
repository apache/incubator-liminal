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

from pathlib import Path

import joblib
from sklearn.linear_model import LinearRegression
from sklearn.pipeline import Pipeline
import numpy as np
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from data_preparation.data_preparation import LABEL_COLUMN, TRAIN_CSV, TEST_CSV
import os
import argparse
import pandas as pd


feature_column_names = [
    'carat',
    'cut',
    'color',
    'clarity',
    'depth',
    'table',
    'x',
    'y',
    'z'
]


categorical_cols = ['cut', 'clarity', 'color']

# inference functions
MODEL_JOBLIB_FILENAME = "model.joblib"

preprocessor = ColumnTransformer(
    transformers=[
        ('categorical',  OneHotEncoder(), categorical_cols)
    ], remainder='passthrough')


def train(train_df, test_df, n_jobs, model_dir):
    X_train = train_df[feature_column_names]
    y_train = train_df[LABEL_COLUMN]

    print(X_train.head(3))
    X_test = test_df[feature_column_names]
    y_test = test_df[LABEL_COLUMN]

    # train

    diamond_price_model=LinearRegression(n_jobs=n_jobs)

    my_pipeline = Pipeline(steps=[
        ('preprocessor', preprocessor),
        ('model', diamond_price_model)
    ])

    my_pipeline.fit(X_train, y_train)

    train_predictions = my_pipeline.predict(X_train)
    print(train_predictions)

    print("validating model")
    abs_err = np.abs(my_pipeline.predict(X_test) - y_test)
    print(f"Test prediction error:{abs_err} ")

    # persist model
    path = os.path.join(model_dir, MODEL_JOBLIB_FILENAME)
    joblib.dump(my_pipeline, path)
    print("model persisted at " + path)
    return path


if __name__ == '__main__':
    data_path = Path(__file__).parent.parent.absolute().joinpath('data')
    parser = argparse.ArgumentParser()
    parser.add_argument('--model-dir', type=str, default=os.getenv('SM_MODEL_DIR', f"file://{data_path}"))
    parser.add_argument('--n-jobs', default=2)
    parser.add_argument("--train", type=str, default=os.getenv("SM_CHANNEL_TRAIN", f"file://{data_path.joinpath('train')}"))
    parser.add_argument("--test", type=str, default=os.getenv("SM_CHANNEL_TEST", f"file://{data_path.joinpath('test')}"))
    parser.add_argument("--train-file", type=str, default=TRAIN_CSV)
    parser.add_argument("--test-file", type=str, default=TEST_CSV)

    args = parser.parse_args()

    train_df = pd.read_csv(os.path.join(args.train, args.train_file))
    test_df = pd.read_csv(os.path.join(args.test, args.test_file))

    train(train_df=train_df, test_df=test_df, n_jobs=args.n_jobs, model_dir=args.model_dir)
