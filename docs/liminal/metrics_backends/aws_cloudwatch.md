<!--
Licensed to the Apache Software Foundation (ASF) under one
or more contributor license agreements.  See the NOTICE file
distributed with this work for additional information
regarding copyright ownership.  The ASF licenses this file
to you under the Apache License, Version 2.0 (the
"License"); you may not use this file except in compliance
with the License.  You may obtain a copy of the License at

  http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing,
software distributed under the License is distributed on an
"AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
KIND, either express or implied.  See the License for the
specific language governing permissions and limitations
under the License.
-->

# aws_cloudwatch metrics backend

The `aws_cloudwatch` metrics backend allows you to send all automatically generated metrics from
your pipelines to AWS CloudWatch.

```yaml
  - metrics_backend: cloudwatch_metrics
    type: aws_cloudwatch
    namespace: DataPipeline
    AWS_REGION_NAME: us-east-1
```

## attributes

`metrics_backend`: name of your metrics backend.

`type`: type of the metrics backend. The current available metrics backends are: `aws_cloudwatch`.

`namespace`: target namespace on AWS CloudWatch.

`AWS_REGION_NAME`: target AWS region to report metrics to.

`AWS_ACCESS_KEY_ID`: AWS access key id (optional).

`AWS_SECRET_ACCESS_KEY`: AWS secret access key (optional).
