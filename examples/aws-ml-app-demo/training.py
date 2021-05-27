import sys
import time

import model_store
import numpy as np
from model_store import ModelStore
from sklearn import datasets
from sklearn.linear_model import LogisticRegression

_CANDIDATE_MODEL_STORE = ModelStore(model_store.CANDIDATE)
_PRODUCTION_MODEL_STORE = ModelStore(model_store.PRODUCTION)


def train_model():
    iris = datasets.load_iris()

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
        train_model()
    elif cmd == 'validate':
        validate_model()
    else:
        raise ValueError(f"Unknown command {cmd}")
