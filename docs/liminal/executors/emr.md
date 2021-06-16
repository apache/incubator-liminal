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

# emr executor

The `emr` executor allows you to run tasks on AWS EMR cluster.

```yaml
  - executor: my_emr_cluster
    type: emr
    cluser_name: liminal-cluster
```

## attributes

`cluster_name`: the name of the cluster uses by the executor

OR

`cluster_id`: the unique identifier of the cluster used by the executor.

`aws_conn_id`: a reference to the emr connection. default: `aws_default`

`cluster_states`: the cluster state filters to apply when searching for an existing cluster.
default: `['RUNNING', 'WAITING']`

`properties`: any attribute of [aws-resource-emr-step-properties](
https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-emr-step.html#aws-resource-emr-step-properties)
(Optional)

## supported task types
- [spark](../tasks/spark.md)
- [sql](../tasks/sql.md)
