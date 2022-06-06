import os
from abc import ABC, abstractmethod
from urllib.parse import urlparse
import sagemaker
import boto3

import shutil


def get_uploader(output_uri_base):
    o = urlparse(output_uri_base)
    if o.scheme == 's3':
        return S3DataUploader()
    elif o.scheme == "file":
        return LocalDataUploader()
    return SagemakerDataUploader()


class DataUploader(ABC):

    def __init__(self):
        pass

    @abstractmethod
    def upload(self, local_path, output_uri_base):
        pass


class LocalDataUploader(DataUploader):
    s3_client = None

    def upload(self, local_path, output_uri_base):
        o = urlparse(output_uri_base)
        os.makedirs(o.path, exist_ok=True)
        shutil.copy2(local_path, o.path)
        return o.path

class S3DataUploader(DataUploader):
    s3_client = None

    def __init__(self):
        self.s3_client = boto3.client('s3')

    def upload(self, local_path, output_uri_base):
        o = urlparse(output_uri_base)
        response = self.s3_client.upload_file(local_path, o.netloc, o.path)


class SagemakerDataUploader(DataUploader):
    sm_client = None
    sm_session = None
    region = None
    default_bucket = None

    def __init__(self):
        self.sm_client = boto3.client("sagemaker")
        self.sm_session = sagemaker.Session()
        self.region = self.sm_session.boto_session.region_name
        self.default_bucket = self.sm_session.default_bucket()

    def upload(self, local_path, output_uri_base):
        o = urlparse(output_uri_base)
        bucket = o.netloc or self.default_bucket
        return self.sm_session.upload_data(
            path=local_path, bucket=bucket, key_prefix=o.path
        )

