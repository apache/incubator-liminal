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
        return self.sm_session.upload_data(path=local_path, bucket=bucket, key_prefix=o.path)
