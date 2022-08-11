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

# Secret Utils

Each `task` in your pipelines has a reference to an secret from the `secrets` section of your
liminal.yml file.

```yaml
---
name: k8s_secret_example
secrets:
  - secret: aws
    path: "~/.aws/credentials"
executors:
  - executor: k8s
    type: kubernetes
variables:
  AWS_CONFIG_FILE: /mnt/credentials
task_defaults:
  python:
    executor: k8s
    image: python:slim-buster
    executors: 2
    mounts:
      - mount: myaws-creds
        volume: aws
        path: /mnt/
pipelines:
  - pipeline: k8s_secret_example
    owner: Bosco Albert Baracus
    start_date: 1970-01-01
    timeout_minutes: 10
    schedule: 0 * 1 * *
    tasks:
      - task: my_python_task
        type: python
        cmd: python --version
```

That example manifest defines a Secret Opaque for AWS credentials used. The values are Base64 strings in the manifest; however, when you use the Secret with a Pod then the kubelet provides the decoded data to the Pod and its containers. \

In order to make use of the AWS credentials we define an environment variable `AWS_CONFIG_FILE` to authenticate our requests.
