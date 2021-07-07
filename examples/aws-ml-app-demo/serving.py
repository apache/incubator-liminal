import json

from flask import jsonify 

import model_store
from model_store import ModelStore

_MODEL_STORE = ModelStore(model_store.PRODUCTION)
_PETAL_WIDTH = 'petal_width'

def predict(input_json):
    print(f'input_json={input_json}')
    input_dict = json.loads(input_json)
    model, version = _MODEL_STORE.load_latest_model()
    if version is None:
        return jsonify(
            message="Model is not ready yet",
            category="fail",
            status=404
        )

    result = str(model.predict_proba([[float(input_dict[_PETAL_WIDTH])]])[0][1])
    print(f'result={result}')
    return jsonify(
        result=result,
        category="success",
        version=f"{version}",
        status=200
    )

def healthcheck(self):
    return 'Server is up!'
