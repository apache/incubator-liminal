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
import logging
import time

from pyspark.accumulators import AccumulatorParam
from pyspark.sql import SparkSession
from pyspark.sql.functions import lit

logger = logging.getLogger()


class ListAccumulator(AccumulatorParam):
    """
    Simple PySpark List accumulator
    """

    def zero(self, value):
        return []

    def addInPlace(self, variable, value):
        if value and value not in variable:
            variable.append(value)

        return variable


class SqlApp:

    def __init__(self, args, spark, version=int(round(time.time()))):
        self.args = args
        self.output_path = args.output_path
        self.output_table = args.output_table
        self.output_format = args.format
        self.query = args.query
        self.partition_columns = args.partition_columns.split(",") if args.partition_columns else []
        self.sub_partition_columns = args.sub_partition_columns.split(
            ",") if args.sub_partition_columns else []
        self.spark = spark
        self.version = version

    def run(self):

        logging.info("Starting Spark SQL job for query: {}".format(self.query))

        logging.info("Output version={}".format(self.version))

        query_result = self.spark \
            .sql(self.query) \
            .withColumn("ver", lit(self.version))

        if self.args.dry_run:
            query_result.show()
        elif self.partition_columns:
            self.__write_with_partitions(df=query_result)
        else:
            self.__write(df=query_result)

    def __write_with_partitions(self, df):
        # write by partitions

        partition_accumulator = self.spark.sparkContext.accumulator([], ListAccumulator())

        df.foreach(self.update_accumulator_with_partitions(self, partition_accumulator))

        partitions = self.partition_columns + ['ver'] + self.sub_partition_columns
        df.repartition(*partitions) \
            .write \
            .partitionBy(partitions) \
            .mode("append") \
            .format(self.output_format) \
            .save(self.output_path)

        self.__update_metastore(partition_accumulator)

    def __write(self, df):

        full_output_path = "{}{}{}".format(self.output_path,
                                           '' if self.output_path.endswith('/') else '/',
                                           self.version)

        logging.info("output data to the following location: {}".format(full_output_path))

        df.write \
            .mode("append") \
            .format(self.output_format) \
            .save(full_output_path)

        self.spark.sql(
            "ALTER TABLE {} SET LOCATION '{}'".format(self.output_table, full_output_path))

    def __update_metastore(self, partition_accumulator):
        partition_specs = [list(zip(self.partition_columns, partition_accumulator_val)) for
                           partition_accumulator_val in partition_accumulator.value]

        for partition_spec in partition_specs:
            location = "{}/".format(self.output_path) + "/".join(
                ["{}={}".format(partition_name, partition_val) for partition_name, partition_val
                 in list(set(partition_spec))]) + "/ver={}".format(self.version)

            partition_spec_comma_delimited = ",".join([
                "{}='{}'".format(partition_name, partition_val) for
                partition_name, partition_val in
                list(set(partition_spec))])

            alter_table_add_partition = \
                "ALTER TABLE {} ADD IF NOT EXISTS PARTITION({}) LOCATION '{}'".format(
                    self.output_table, partition_spec_comma_delimited, location)

            logging.info("Start update table with: {}".format(alter_table_add_partition))

            self.spark.sql(alter_table_add_partition)

            logging.info("Finish to update table with: {}".format(alter_table_add_partition))

            alter_table_set_partition_location = "ALTER TABLE {} PARTITION({}) SET LOCATION '{}'" \
                .format(self.output_table,
                        partition_spec_comma_delimited,
                        location)

            logging.info(
                "Start update table with: {}".format(alter_table_set_partition_location))

            self.spark.sql(alter_table_set_partition_location)

            logging.info(
                "Finish to update table with: {}".format(alter_table_set_partition_location))

    @staticmethod
    def update_accumulator_with_partitions(sql_task, partition_accumulator):
        partition_columns = sql_task.partition_columns

        def _update_accumulator_with_partitions(row):
            for column in partition_columns:
                partition_accumulator.add(row.asDict()[column])

        return _update_accumulator_with_partitions


def __parse_arguments():
    parser = argparse.ArgumentParser(description='Liminal Sql App')
    parser.add_argument('--app_name', metavar='app_name', type=str, help='application name',
                        required=True)
    parser.add_argument('--query', metavar='query', type=str, help='sql query', required=True)
    parser.add_argument('--output_path', metavar='output_path', type=str, help='output path',
                        required=True)
    parser.add_argument('--output_table', metavar='output_table', type=str, help='output table',
                        required=True)
    parser.add_argument('--format', metavar='format', type=str, help='output format',
                        default="parquet", required=False)
    parser.add_argument('--partition_columns', metavar='partition_columns', help='dry run flag',
                        default="",
                        required=False)
    parser.add_argument('--sub_partition_columns', metavar='partition_columns', help='dry run flag',
                        default="",
                        required=False)
    parser.add_argument('--dry_run', metavar='dry_run', type=bool, help='dry run flag',
                        default=False, required=False)

    return parser.parse_args()


def __init_spark_session(args):
    return SparkSession \
        .builder \
        .appName(args.app_name) \
        .enableHiveSupport() \
        .getOrCreate()


if __name__ == "__main__":
    arguments = __parse_arguments()
    spark_session = __init_spark_session(arguments)
    SqlApp(arguments, spark_session).run()
    spark_session.stop()
