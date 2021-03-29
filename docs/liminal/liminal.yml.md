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

## liminal.yml

Definition of your own liminal system is done via yml configuration file named liminal.yml in
your project. This yml is the one place in which you define all characteristics and behavior of your
liminal system.
In this section we'll go over the anatomy of the liminal.yml file.

### root attributes

At the root level of your limimal.yml you can define the most basic root characteristics of your
liminal system such as name and owner:

```yaml
name: MyLiminalSystem
owner: Bosco Albert Baracus
```

### images

For fully detailed information on pipelines see: [images](images).

In the `images` section you can configure how to pack your code into docker images. This can be
achieved in liminal easily, without any Docker knowledge needed by setting just a few attributes:

```yaml
images:
  - image: myorg/myrepo:mypythonapp
    type: python
    source: .
  - image: myorg/myrepo:myserver
    type: python_server
    source: path/to/my/server/code 
    endpoints:
      - endpoint: /myendpoint
        module: my_module
        function: my_function
```

`images` is a section in the root lof your liminal.yml file and is a list of `image`s, defined 
by the following attributes:

#### image attributes

`image`: name of your image, usually will be in the form of `user/repository:tag` common in docker
image repositories such as Docker Hub, but for local development this can be any string.

`type`: type of the image. Usually this will match your coding language, or your coding langauge
followed by an `_` and a specific style of application (such as a server).
The current available image types are: `python`.

`source`: location of source files to include in the image, this can be a relative path within your
project, or even `.` which means the entire project should be packaged in the image.

`build_cmd`: certain languages require to be built or compiled, here you can provide your build
command to be executed in order to build your code.

Other image types might require additional configuration, for example, servers require `endpoints`
to be configured.

### pipelines

For fully detailed information on pipelines see: [pipelines](pipelines.md).

In the `pipelines` section you can configure scheduled/manually run pipelines of tasks to be
executed sequentially:

```yaml
pipelines:
  - pipeline: my_data_pipeline
    timeout_minutes: 30
    start_date: 2020-03-01
    schedule: 0 10 * * *
    tasks:
      - task: my_sql_task
        type: sql
        query: "SELECT * FROM
        {{my_database_name}}.{{my_table_name}}
        WHERE event_date_prt >= 
              '{{yesterday_ds}}'"
              AND cms_platform = 'xsite'          
        output_table: my_db.my_out_table
        output_path: s3://my_bky/{{env}}/mydir
      - task: my_python_task
        type: python
        image: myorg/myrepo:pythonapp
        cmd: python my_python_app.py
        env_vars:
          env: {{env}}
          fizz: buzz
      - task: my_python_task
        type: python
        image: myorg/myrepo:mypythonapp
        cmd: python -u my_module.py
        env_vars:
          env: {{env}}
          fizz: buzz
```

`pipelines` is a section in the root lof your liminal.yml file and is a list of `pipeline`s defined 
by the following attributes:

#### pipeline attributes

`pipeline`: name of your pipeline (must be unique per liminal server).

`timeout_minutes`: maximum allowed pipeline run time in minutes, if run exceeds this time, pipeline
and all running tasks will fail.

`start_date`: start date for the pipeline.

`schedule`: to be configured if the pipeline should run on a schedule. Format is
[cron expression](https://en.wikipedia.org/wiki/Cron#CRON_expression).

`tasks`: list of `task`s, defined by the following attributes:

##### task attributes

For fully detailed information on tasks see: [tasks](tasks).

`task`: name of your task (must be made of alphanumeric, dash and/or underscore characters only).

`type`: type of the task. Examples of available task types are: `python`.
and more..

Different task types require their own additional configuration. For example, `python` task requires
`image` to be configured.

### services

For fully detailed information on services see: [services](services.md).

In the `services` section you can configure constantly running applications such as
servers. 

```yaml
services:
  - service: my_server
    image: myorg/myrepo:myserver
```

`services` is a section in the root lof your liminal.yml file and is a list of `service`s, defined 
by the following attributes:

#### service attributes

`service`: name of your service.

`image`: the service's docker image.

### monitoring

For fully detailed information on monitoring see: [monitoring](monitoring.md).

In the `monitoring` section you can configure monitoring for your pipelines and services. 

```yaml
monitoring:
  metrics_backends:
    - metrics_backend: cloudwatch_metrics
      type: aws_cloudwatch
      namespace: DataPipeline
      AWS_REGION_NAME: us-east-1
  alerts_backends:
    - alerts_backend: cloudwatch_alerts
      type: aws_cloudwatch
      metrics_backend: cloudwatch_metrics
      ok_actions: ['arn:aws:sns:...']
      alarm_actions: ['arn:aws:sns:...']
```

`monitoring` is a section in the root lof your liminal.yml file and is a list of `metrics_backend`s and
a  list of `alerts_backend`s.

`metrics_backend`s are where metrics for your pipelines are automatically sent.

`alerts_backends`s automatically register alerts based on `metrics_backend` they are paired with.

#### metrics_backend attributes

`metrics_backend`: name of your metrics backend

`type`: type of the metrics backend. The current available metrics backends are: `aws_cloudwatch`.

Different metrics backend types require their own additional configuration. For example,
`aws_cloudwatch` metrics backend requires `namespace` to be configured.

#### alerts_backend attributes

`alerts_backend`: name of your alerts backend

`type`: type of the alerts backend. The current available alerts backends are: `aws_cloudwatch`.

`metrics_backend`: name of the metrics backends to register alerts for.

Different alerts backend types require their own additional configuration. For example,
`aws_cloudwatch` alerts backend requires `alarm_actions` to be configured.

### advanced topics

For documentation of more advanced features of liminal.yml see:
[advanced liminal.yml](advanced.liminal.yml.md)
