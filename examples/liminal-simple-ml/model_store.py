import pickle
import time

import boto3, os

AWS_DEFAULT_BUCKET = os.environ.get(AWS_DEFAULT_BUCKET, 'ml-ab-dev')
PRODUCTION = 'production'
CANDIDATE = 'candidate'

_ONE_HOUR = 60 * 60


class ModelStore:

    def __init__(self, env):
        self.env = env
        self._latest_model = None
        self._latest_version = None
        self._last_check = time.time()
        self._s3 = boto3.client('s3')

    def load_latest_model(self, force=False):
        if not self._latest_model or time.time() - self._last_check > _ONE_HOUR or force:
            self._latest_model, self._latest_version = self._download_latest_model()

        return self._latest_model, self._latest_version

    def save_model(self, model, version):
        pickle.dump(model, open("/tmp/model.p", "wb"))

        model_pkl = open("/tmp/model.p", "rb").read()
        s3_key = f'{self.env}/{version}/model.p'
        self._s3.put_object(Bucket=AWS_DEFAULT_BUCKET, Key=s3_key, Body=model_pkl)

    def _download_latest_model(self):
        file_path = '/tmp/downloaded_model.p'
        s3_objects = self._s3.list_objects(Bucket=AWS_DEFAULT_BUCKET, Prefix=self.env)['Contents']
        models = list(
            reversed(sorted([obj['Key'] for obj in s3_objects if obj['Key'].endswith('.p')]))
        )
        latest_s3_key = models[0]
        version = latest_s3_key.split('/')[1]
        print(f'Loading model version {version}')
        self._s3.download_file(AWS_DEFAULT_BUCKET, latest_s3_key, file_path)
        return pickle.load(open(file_path, 'rb')), version
