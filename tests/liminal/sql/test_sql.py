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
from unittest import TestCase

from pyspark.sql import SparkSession
from pyspark.sql.functions import lit
from pyspark_test import assert_pyspark_df_equal

from liminal.sql.sql_app import SqlApp


class TestSparkSql(TestCase):
    """
    Test Spark Sql Code
    """
    IMPRESSION_TABLE_NAME = "impression"
    OUTPUT_TABLE_NAME = "output"
    OUTPUT_DIM_TABLE_NAME = "my_dim"
    OUTPUT_SUB_TABLE_NAME = "my_sub_table"
    VERSION = 123

    def setUp(self) -> None:
        super().setUp()
        self.input_dir = os.path.dirname(__file__)
        self.output_dir = os.path.abspath("/tmp/liminal-sql-test/")

        self.spark_session = SparkSession \
            .builder.master("local") \
            .appName("test-liminal-sql-app") \
            .config('spark.driver.extraJavaOptions', '-Dderby.system.home=/tmp/derby') \
            .enableHiveSupport().getOrCreate()

    def test_sql_etl_write_with_sub_partitions(self):
        output_sub_table_dir = f"{self.output_dir}/output/{self.OUTPUT_TABLE_NAME}"

        self.__set_up_arguments(output_path=f"file://{output_sub_table_dir}",
                                output_table=self.OUTPUT_SUB_TABLE_NAME,
                                query="select * from my_source",
                                formatz="parquet", partition_column="action_time_prt",
                                sub_partition_columns="type,bibi,sara")

        self.__set_up_output_sub_table()

        self.sql_app = SqlApp(args=self.args, spark=self.spark_session, version=self.VERSION)

        df_source = [
            ("1", "A", "2014-01-01", "a", "a"),
            ("2", "A", "2014-01-01", "a", "a"),
            ("3", "A", "2014-10-13", "a", "a"),
            ("4", "B", "2014-11-30", "b", "b")
        ]

        columns = ["id", "type", "action_time_prt", "bibi", "sara"]

        self.spark_session.createDataFrame(df_source, columns).createOrReplaceTempView("my_source")

        self.sql_app.run()

        self.assertTrue(
            os.listdir(
                f"{output_sub_table_dir}/action_time_prt=2014-11-30/ver=123/type=B/bibi=b/sara=b"))
        self.assertTrue(
            os.listdir(
                f"{output_sub_table_dir}/action_time_prt=2014-01-01/ver=123/type=A/bibi=a/sara=a"))
        self.assertTrue(
            os.listdir(
                f"{output_sub_table_dir}/action_time_prt=2014-10-13/ver=123/type=A/bibi=a/sara=a"))

    def test_sql_etl_write_table_with_partitions(self):
        output_dir_path = f"file://{self.output_dir}/output/impressions_results/"

        self.__set_up_impression_table()
        self.__set_up_output_table()

        self.__set_up_arguments(output_path=output_dir_path,
                                output_table=self.OUTPUT_TABLE_NAME,
                                query=
                                f"select dt, data.cms_site as cms_site, data.uid as uid,"
                                f" data.iid as iid from {self.IMPRESSION_TABLE_NAME}",
                                formatz="parquet", partition_column="dt")

        self.sql_app = SqlApp(args=self.args, spark=self.spark_session)

        self.sql_app.run()

        actual_query_result = self.spark_session.sql(f"select * from {self.OUTPUT_TABLE_NAME}")

        expected_query_result = self.spark_session.read.json(
            f"file://{self.input_dir}/data/expected/expected_table.json")

        assert_pyspark_df_equal(actual_query_result.sort("dt", "iid", "uid", "cms_site"),
                                expected_query_result.sort("dt", "iid", "uid", "cms_site"))

    def test_sql_write_table(self):
        output_dit_path = f"file://{self.output_dir}/output/{self.OUTPUT_DIM_TABLE_NAME}"

        self.__set_up_dim_tables()
        df_source = [
            ("1", "A", "2014-01-01T23:00:01.000+0000"),
            ("1", "A", "2014-01-01T23:00:01.000+0000"),
            ("1", "A", "2014-10-13T12:40:32.000+0000"),
            ("1", "A", "2014-11-30T12:40:32.000+0000"),
            ("2", "A", "2016-12-29T09:54:00.000Z"),
            ("2", "A", "2016-05-09T10:12:43.000+0000")
        ]

        columns = ["id", "type", "action_time"]

        self.spark_session.createDataFrame(df_source, columns).createOrReplaceTempView(
            "my_source_dim")
        self.__set_up_arguments(output_path=output_dit_path,
                                output_table=self.OUTPUT_DIM_TABLE_NAME,
                                query="select id,type,action_time from my_source_dim")

        self.sql_app = SqlApp(args=self.args, spark=self.spark_session, version=self.VERSION)

        self.sql_app.run()

        actual_query_result = self.spark_session.sql(f"select * from {self.OUTPUT_DIM_TABLE_NAME}")

        expected_query_result = self.spark_session.read.json(
            f"file://{self.input_dir}/data/expected/expected_dim_table.json")

        assert_pyspark_df_equal(actual_query_result, expected_query_result)

    def __set_up_dim_tables(self):
        output_dim_table = self.OUTPUT_DIM_TABLE_NAME
        self.spark_session.sql(f"DROP TABLE IF EXISTS {output_dim_table}")
        self.spark_session.sql(
            f"""CREATE TABLE `{output_dim_table}`(id string, type string, action_time string) 
            STORED AS PARQUET""")

    def __set_up_output_table(self):
        output_table = self.OUTPUT_TABLE_NAME

        self.spark_session.sql(f"DROP TABLE IF EXISTS {output_table}")
        self.spark_session.sql(
            f"""CREATE TABLE `{output_table}`(
                         `cms_site` long, `uid` string, `iid` string
                       )
                       PARTITIONED BY (`dt` string) STORED AS PARQUET""")

    def __set_up_output_sub_table(self):
        output_sub_table = self.OUTPUT_SUB_TABLE_NAME
        self.spark_session.sql(f"DROP TABLE IF EXISTS {output_sub_table}")
        self.spark_session.sql(
            f"""CREATE TABLE `{output_sub_table}`(id string, type string, action_time string)
             PARTITIONED BY (action_time_prt string) STORED AS PARQUET""")

    def __set_up_impression_table(self):
        self.spark_session.read \
            .json(f'file://{self.input_dir}/data/impression/dt=2018-12-11/hh=00') \
            .withColumn("dt", lit("2018-12-11")) \
            .union(self.spark_session
                   .read.json(f'file://{self.input_dir}/data/impression/dt=2018-12-12/hh=00')
                   .withColumn("dt", lit("2018-12-12"))) \
            .createOrReplaceTempView(self.IMPRESSION_TABLE_NAME)

    def __set_up_arguments(self, output_path, output_table, query, formatz="parquet",
                           partition_column="",
                           sub_partition_columns="", dry_run=False):
        self.args = argparse.ArgumentParser(description='Liminal Test Sql App')

        self.args.output_path = output_path
        self.args.output_table = output_table
        self.args.query = query
        self.args.format = formatz
        self.args.partition_columns = partition_column
        self.args.sub_partition_columns = sub_partition_columns
        self.args.dry_run = dry_run
