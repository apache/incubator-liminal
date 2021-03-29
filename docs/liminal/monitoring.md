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

# Monitoring

In the `monitoring` section you can configure monitoring for your pipelines and services. 

```yaml
monitoring:
  metrics_backends:
    - metrics_backend: cloudwatch_metrics
      type: aws_cloudwatch
      namespace: DataPipeline
      AWS_REGION_NAME: us-east-1
```

`monitoring` is a section in the root lof your liminal.yml file and is a list of `metrics_backend`s and
a  list of `alerts_backend`s.

`metrics_backend`s are where metrics for your pipelines are automatically sent.

`alerts_backends`s automatically register alerts based on `metrics_backend` they are paired with.

## metrics_backend attributes

For fully detailed information on metrics backends see: [metrics backends](metrics_backends).

`metrics_backend`: name of your metrics backend

`type`: type of the metrics backend. The current available metrics backends are: `aws_cloudwatch`.

Different metrics backend types require their own additional configuration. For example,
`aws_cloudwatch` metrics backend requires `namespace` to be configured.
