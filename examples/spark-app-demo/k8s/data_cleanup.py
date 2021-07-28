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

import sys

from pyspark.sql import SparkSession

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: source <file> destination <dest>", file=sys.stderr)
        sys.exit(-1)

    spark = SparkSession \
        .builder \
        .appName("CleanData") \
        .getOrCreate()

    spark.read.text(sys.argv[1]).rdd.filter(lambda x: not x[0].startswith('#')) \
        .filter(lambda r: not r[0].startswith('ignore')) \
        .map(lambda r: r[0]).map(
        lambda r: (
            r.split(',')[0], r.split(',')[1], r.split(',')[2], r.split(',')[3], r.split(',')[4])) \
        .toDF().coalesce(1).write.mode("overwrite").option("header", "false").csv(sys.argv[2])

    spark.stop()
