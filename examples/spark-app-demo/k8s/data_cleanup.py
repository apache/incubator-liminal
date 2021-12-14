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

import pyspark.sql.functions as F
from pyspark.ml import Pipeline
from pyspark.ml.feature import StringIndexer, VectorAssembler, StandardScaler
from pyspark.ml.functions import vector_to_array
from pyspark.sql import SparkSession


def transform(data):
    columns_to_scale = data.columns[:-1]
    vectorizer = VectorAssembler(inputCols=columns_to_scale, outputCol="features")
    scaler = StandardScaler(inputCol="features", outputCol="scaled_features", withStd=True, withMean=True)
    labeler = StringIndexer(inputCol=data.columns[-1], outputCol='label')
    pipeline = Pipeline(stages=[vectorizer, scaler, labeler])
    fitted = pipeline.fit(data)
    transformed = fitted.transform(data)

    result = transformed.withColumn("feature_arr", vector_to_array("scaled_features")).select(
        [F.col("feature_arr")[i].alias(columns_to_scale[i]) for i in range(len(columns_to_scale))] + ['label']
    )

    return result


def extract(spark, input_uri):
    return spark.read.csv(input_uri, header=True, inferSchema=True, comment="#")


def load(data, output_uri):
    data.coalesce(1).write.mode("overwrite").csv(output_uri, header=True)


def data_pipeline(input_uri, output_uri):
    spark = SparkSession.builder.appName("Prepare Iris Data").getOrCreate()

    input = extract(spark, input_uri)
    data = transform(input)
    load(data, output_uri)
    spark.stop()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_uri")
    parser.add_argument("--output_uri")
    args = parser.parse_args()
    data_pipeline(args.input_uri, args.output_uri)
