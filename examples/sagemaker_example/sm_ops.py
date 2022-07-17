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
import time

import boto3
import numpy as np
import pandas as pd
import sagemaker
from sagemaker.sklearn.estimator import SKLearn
from sagemaker.sklearn.model import SKLearnModel

from data_preparation.data_preparation import (data_pipeline,
                                               DATASET_PUBLIC_URL,
                                               LABEL_COLUMN)
from data_preparation.data_uploader import SagemakerDataUploader
from data_train.train import feature_column_names

FRAMEWORK_VERSION = "0.23-1"

sm_boto3 = boto3.client("sagemaker")


def get_role():
    try:
        role = sagemaker.get_execution_role()
    except ValueError:
        role = os.getenv("SM_ROLE")
    return role


def sm_train(train_path, test_path, base_job_name="Liminal-sm-training-job", instance_type="ml.m5.large", n_jobs=1):
    sklearn_estimator = SKLearn(
        entry_point="data_train/train.py",
        source_dir="./",
        role=get_role(),
        instance_count=1,
        instance_type=instance_type,
        framework_version=FRAMEWORK_VERSION,
        base_job_name=base_job_name,
        hyperparameters={
            "n-jobs": n_jobs,
        }
    )
    sklearn_estimator.fit({"train": train_path, "test": test_path})
    artifact = sm_boto3.describe_training_job(
        TrainingJobName=sklearn_estimator.latest_training_job.name
    )["ModelArtifacts"]["S3ModelArtifacts"]

    print("Model artifact persisted at " + artifact)
    return artifact


def sm_deploy(artifact, model_name="Liminal-sm-demo-model", instance_type="ml.m5.large"):

    timestamp = time.strftime("-%Y-%m-%d-%H-%M-%S", time.gmtime())
    model = SKLearnModel(
        name=f"{model_name}-{timestamp}",
        entry_point="inference.py",
        model_data=artifact,
        role=get_role(),
        framework_version=FRAMEWORK_VERSION,
    )

    predictor = model.deploy(instance_type=instance_type, initial_instance_count=1, wait=True)
    return predictor


def sm_validate(predictor, test_path):
    if not test_path.startswith("s3"):
        test_path = f"s3://{test_path}"

    df = pd.read_csv(test_path)
    X_test_inference = df[feature_column_names].to_numpy()
    predictions = predictor.predict(data=X_test_inference)
    print("validating model")
    avg_err = np.average(np.abs(predictions - df[LABEL_COLUMN]))
    print(f"average abs error:{avg_err}")
    print(predictions)
    return avg_err


def sm_data_prep(input_uri, output_uri_base):
    return data_pipeline(input_uri=input_uri or DATASET_PUBLIC_URL, output_uri_base=output_uri_base,
                  data_uploader=SagemakerDataUploader())


def sm_main(args):
    test_path = 'sagemaker-us-east-1-468326661668/liminal-sm-example/test/diamonds_test.csv'
    train_path, test_path = sm_data_prep(args.input_uri, args.output_uri_base)
    artifact = sm_train(train_path, test_path,  base_job_name=args.base_job_name, instance_type=args.train_instance_type, n_jobs=args.n_jobs)
    #artifact = 's3://sagemaker-us-east-1-468326661668/Liminal-sm-training-job-2022-06-06-14-30-39-827/output/model.tar.gz'
    predictor = sm_deploy(artifact, model_name=args.model_name, instance_type=args.deploy_instance_type)
    #predictor =  Predictor(endpoint_name="Liminal-sm-demo-model-2022-06-06-14-35-48-079", serializer=NumpySerializer(), deserializer=NumpyDeserializer())
    sm_validate(predictor, test_path)


def create_sm_args_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_uri",
                        default=DATASET_PUBLIC_URL)
    parser.add_argument("--output_uri_base",
                        default="liminal-sm-example")
    parser.add_argument("--base_job_name",
                        default="Liminal-sm-training-job")
    parser.add_argument("--train_instance_type", default="ml.m5.large")
    parser.add_argument("--n_jobs", default=1)
    parser.add_argument("--model_name",
                        default="Liminal-sm-demo-model")
    parser.add_argument("--deploy_instance_type", default="ml.m5.large")
    return parser


if __name__ == '__main__':
    parser = create_sm_args_parser()
    args = parser.parse_args()
    sm_main(args)
