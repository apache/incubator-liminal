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

# spark task

The `spark` task allows you to submit a spark application

```yaml
  - task: my_spark_app
    type: spark
    executor: emr_executor
    application_source: 'my_app.py',
    class: 'com.mycompany.MySparkApp',
    master: 'yarn',
    conf:
      spark.driver.memory: '1g',
      spark.driver.maxResultSize: '1g',
      spark.yarn.executor.memoryOverhead: '500M'
    application_arguments:
      --query: "select * from my_db.my_input_table where my_date_col >= "
                 "'{{yesterday_ds}}'",
      --output: 'my_output_table'
```

## attributes

`task`: name of your task (must be made of alphanumeric, dash and/or underscore characters only).

`executor`: executor name ([supported executors](#supported-executors))

`application_source`: the location of the spark application (jar location / python file)

`class`: the entry point for your application

`master`: the cluster manager to connect to.See the list
of [allowed master URL's](https://spark.apache.org/docs/latest/submitting-applications.html#master-urls)
(Optional)

`conf`: arbitrary Spark configuration properties (Optional)

`application_arguments`: arguments passed to the main method of your main class (Optional)

## supported executors
- [emr](../executors/emr.md)
- [kubernetes](../executors/kubernetes.md)
