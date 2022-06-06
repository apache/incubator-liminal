import argparse
import os
import pandas as pd
from sklearn.model_selection import train_test_split
from data_preparation.data_uploader import get_uploader
from pathlib import Path

TEST_CSV = "diamonds_test.csv"

TRAIN_CSV = "diamonds_train.csv"

LABEL_COLUMN = 'price'

DATASET_PUBLIC_URL="https://www.openml.org/data/get_csv/21792853/dataset"

def transform(data):
    X = data.drop(columns=LABEL_COLUMN)
    y = data[LABEL_COLUMN]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3,
                                                        random_state=42)
    train = X_train.copy()
    train[LABEL_COLUMN] = y_train

    test = X_test.copy()
    test[LABEL_COLUMN] = y_test
    return train, test


def extract(input_uri):
    return pd.read_csv(input_uri)


def load(train, test, output_uri_base, data_uploader):
    train.to_csv(TRAIN_CSV)
    test.to_csv(TEST_CSV)
    train_path = data_uploader.upload(TRAIN_CSV, os.path.join(output_uri_base, "train"))
    test_path = data_uploader.upload(TEST_CSV, os.path.join(output_uri_base, "test"))
    return train_path, test_path


def data_pipeline(input_uri, output_uri_base, data_uploader):
    data = extract(input_uri)
    train, test = transform(data)
    return load(train, test, output_uri_base, data_uploader)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_uri",
                        default=DATASET_PUBLIC_URL)
    parser.add_argument("--output_uri_base",
                        default=f"file://{Path(__file__).parent.parent.absolute().joinpath('data')}",
                        help="a uri starting with 's3', 'file' or a relative path "
                             "which will be treated as sagemaker prefix")
    args = parser.parse_args()
    data_uploader = get_uploader(args.output_uri_base)
    data_pipeline(args.input_uri, args.output_uri_base, data_uploader)
