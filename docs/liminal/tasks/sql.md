<!--
Licensed to the Apache Software Foundation (ASF) under one
or more contributor license agreements.  See the NOTICE file
distributed with this work for additional information
regarding copyright ownership.  The ASF licenses this file
to you under the Apache License, Version 2.0 (the
"License"); you may not use this file except in compliance
with the License.  You may obtain a copy of the License at

  http://www.apache.org/licenses/LICENSE-2.0

Unless required bgit y applicable law or agreed to in writing,
software distributed under the License is distributed on an
"AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
KIND, either express or implied.  See the License for the
specific language governing permissions and limitations
under the License.
-->

# sql task

The `sql` task allows you to submit a spark SQL query

```yaml
  - task: my_sql_app
    type: sql
    executor: emr_executor
    output_table: default.my_output_table
    output_path: s3://my-liminal/output/
    query: "select * from my_db.my_input_table where my_date_col >= "
             "'{{yesterday_ds}}'"
```

## attributes

`task`: name of your task (must be made of alphanumeric, dash and/or underscore characters only).

`executor`: executor name ([supported executors](spark.md#supported-executors))

`output_table`: name of the output table

`output_path`: output path location

`format`: output format (e.g. json, parquet, csv). default: parquet (Optional)

`partition_columns`: comma separated list of the output table partition columns names (Optional)

`sub_partition_columns`: comma seperated list of undocumented partition columns (Optional)
