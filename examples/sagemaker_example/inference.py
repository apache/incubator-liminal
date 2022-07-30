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

import argparse
import os
from io import BytesIO
import pandas as pd
import numpy as np

import joblib


feature_column_names = ['carat', 'cut', 'color', 'clarity', 'depth', 'table', 'x', 'y', 'z']


categorical_cols = ['cut', 'clarity', 'color']

MODEL_JOBLIB_FILENAME = "model.joblib"


def model_fn(model_dir):
    clf = joblib.load(os.path.join(model_dir, MODEL_JOBLIB_FILENAME))
    return clf


def input_fn(input_data, content_type):
    if content_type == "application/x-npy":
        load_bytes = BytesIO(input_data)
        input_np = np.load(load_bytes, allow_pickle=True)
        df = pd.DataFrame(data=input_np, columns=feature_column_names)
        return df
    else:
        raise ValueError(
            f"content type {content_type} is not supported by this inference endpoint. Please send a legal application/x-npy payload"
        )


def predict_fn(input_data, model):
    prediction = model.predict(input_data[feature_column_names])
    return prediction


def df_to_inference_input():
    X_train = df[feature_column_names]
    rows = X_train.head(10)
    inference_input = rows.to_numpy()
    np_bytes = BytesIO()
    np.save(np_bytes, inference_input, allow_pickle=True)
    input_data = input_fn(np_bytes.getvalue(), "application/x-npy")
    return input_data


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model-dir", type=str, default=os.getenv("SM_MODEL_DIR", "../data"))
    parser.add_argument("--data-path", type=str, default=f"../data/test/diamonds_test.csv")
    args = parser.parse_args()
    model = model_fn(args.model_dir)
    df = pd.read_csv(args.data_path)
    input_data = df_to_inference_input()
    predictions = predict_fn(input_data, model)
    print(predictions)
