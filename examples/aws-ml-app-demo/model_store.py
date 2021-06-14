import pickle
import time
import glob

import os

MOUNT_PATH = os.environ.get('MOUNT_PATH', '/mnt/gettingstartedvol')
PRODUCTION = 'production'
CANDIDATE = 'candidate'

_ONE_HOUR = 60 * 60

class ModelStore:

    def __init__(self, env):
        self.env = env
        self._latest_model = None
        self._latest_version = None
        self._last_check = time.time()

    def load_latest_model(self, force=False):
        if not self._latest_model or time.time() - self._last_check > _ONE_HOUR or force:
            self._latest_model, self._latest_version = self._download_latest_model()

        return self._latest_model, self._latest_version

    def save_model(self, model, version):
        s3_key = 'model.p'
        s3_dir = f'{MOUNT_PATH}/{self.env}/{version}'

        os.makedirs(f'{s3_dir}', exist_ok=True)
        pickle.dump(model, open(f'{s3_dir}/{s3_key}', "wb"))

    def _download_latest_model(self):
        s3_objects = (glob.glob(f'{MOUNT_PATH}/{self.env}/**/*'))
        models = list(reversed(sorted([obj for obj in s3_objects if obj.endswith('.p')])))
        latest_s3_key = models[0]
        version = latest_s3_key.rsplit('/')[-2]
        print(f'Loading model version {version}')
        return pickle.load(open(latest_s3_key, 'rb')), version
