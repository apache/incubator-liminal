import json

import model_store
from model_store import ModelStore

_MODEL_STORE = ModelStore(model_store.PRODUCTION)
_PETAL_WIDTH = 'petal_width'


def predict(input_json):
    try:
        input_dict = json.loads(input_json)
        model, version = _MODEL_STORE.load_latest_model()
        result = str(model.predict_proba([[float(input_dict[_PETAL_WIDTH])]])[0][1])
        return json.dumps({"result": result, "version": version})

    except IndexError:
        return 'Failure: the model is not ready yet'

    except Exception as e:
        print(e)
        return 'Failure'


def healthcheck(self):
    return 'Server is up!'


def version(self):
    try:
        model, version = _MODEL_STORE.load_latest_model()
        print(f'version={version}')
        return version
    except Exception as e:
        return e
