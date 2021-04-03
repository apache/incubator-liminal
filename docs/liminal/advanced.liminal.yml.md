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

# Advanced liminal.yml

In this section you will learn about advanced features of liminal.yml

## Variables

Much like in programming languages, you can define variables for re-use across your liminal.yml file.

```yaml
variables:
  myvar1: myvalue1
  myvar2: myvalue2
```

In the `variables` section of your liminal.yml you can define your variables as key value pairs

## Placeholders

You can use placeholders of format `{{myplaceholder}}` in most any string value in your liminal.yml Make sure that any
string that includes placeholders is surrounded by single or double quotes.

For example:

```yaml
variables:
  image_name: myorg/myrepo:myapp
images:
  - image: '{{image_name}}'
    type: python
    source: .
pipelines:
  - pipeline: my_pipeline
    tasks:
      - task: my_python_task
        type: python
        image: "{{image_name}}"
        cmd: python -u my_module.py
```

### Placeholders rendering

The process of rendering placeholders checks for values in several places, by order.

#### Pipeline placeholder rendering

When running pipelines placeholders will be rendered by replacing values from sources in the following order:

1. Current [DAG run conf](https://airflow.apache.org/docs/apache-airflow/stable/dag-run.html)
   (Airflow).
2. liminal.yml [variables](#variables) section.
3. [Airflow variables](https://airflow.apache.org/docs/apache-airflow/stable/howto/variable.html)
   (Airflow).
4. [Airflow macros](https://airflow.apache.org/docs/apache-airflow/stable/macros-ref.html) (Airflow)
   . For example: `"{{yesterday_ds}}"`. For more information see:
5. Airflow [Jinja Templating](https://airflow.apache.org/docs/apache-airflow/stable/concepts.html#jinja-templating)
   (Airflow).

#### Build placeholder rendering

When using `liminal build` placeholders will be rendered by replacing values from sources in the following order:

1. Environment variables.
2. liminal.yml [variables](#variables) section.

## Task variables

In addition to the variables section you can also set specific variables for specific `task`s using the `variables`
attribute of that task. For example:

```yaml
  - task: my_task
    type: python
    cmd: python -u my_module.py
    variables:
      myvar1: myvalue1
      myvar2: myvalue2
```

You can also pass a reference to a variable map (dictionary) set in your variables section:

```yaml
variables:
  my_variable_map:
    myvar1: myvalue1
    myvar2: myvalue2
  my_variable_map2:
    myvar1: myvalue_a
    myvar2: myvalue_x
pipelines:
  - pipeline: my_pipeline
    tasks:
      - task: my_task1
        type: python
        cmd: python -u my_module.py
        variables: my_variable_map1
      - task: my_task2
        type: python
        cmd: python -u my_module.py
        variables: my_variable_map2
```

## Executors

For fully detailed information on executors see: [executors](executors).

Each `task` in your pipelines has a reference to an executor from the `executors` section of your liminal.yml file. If
not specified, the appropriate default executor for that task type is used.

```yaml
executors:
  - executor: my_kubernetes_executor
    type: kubernetes
    resources:
      request_memory: 128Mi
pipelines:
  pipeline: my_pipeline
  tasks:
    - task: my_python_task
      type: python
      image: myorg/myrepo:mypythonapp
      executor: my_kubernetes_executor
      cmd: python -u my_module.py
```

In the example above we define an `executor` of type `kubernetes` with custom resources configuration.

`executors` is a section in the root of your liminal.yml file and is a list of `executor`s defined by the following
attributes:

### executor attributes

`executor`: name of your executor.

`type`: type of the executor. The current available image types are: `kubernetes` and `emr`.

Different executor types support their own additional configuration.

## Task Defaults

`task_defaults` is a section in the root of your liminal.yml file in which default attributes can be set for each `task`
type.

```yaml
task_defaults:
  python:
    executor: my_kubernetes_executor
    env_vars:
      env: {{env}}
      foo: bar
```

In the example above we set default attributes for any `python` task in any pipeline in the liminal system defined by
our liminal.yml file. Each `python` task that does not set these attributes will default to the setting
in `task_defaults`.

If the same attribute is defined in both `task_defaults` and in the `task`, definitions from the
`task` take precedence. If a map (dictionary) of values (for example `env_vars`) is defined in both
`task_defaults` the two maps will be merged, with definitions in the `task` taking precedence in case key is defined in
both maps.

## Pipeline Defaults

`pipeline_defaults` is a section in the root of your liminal.yml file in which default attributes can be set for
each `pipeline` in the liminal system defined in your liminal.yml file.

```yaml
pipeline_defaults:
  start_date: 2021-01-01
  timeout_minutes: 30
```

In the example above we set default attributes for any `pipeline` defined in our liminal.yml file. Each `pipeline` that
does not set these attributes will default to the setting in
`pipeline_defaults`.

If the same attribute is defined in both `pipeline_defaults` and in the `pipeline`, definitions from the `pipeline` take
precedence.

If `tasks` section is defined in `pipeline_defaults` each pipeline defined in our liminal.yml file will have the tasks
defined in `pipeline_defaults`.

A special `task` type `pipeline` may be used in `pipeline_defaults` `tasks` section. This task type is interpreted as "
tasks defined in pipeline go here". This allows flexibility of defining common tasks to be run before and after the
tasks of each pipeline defined in our liminal.yml file. For example:

```yaml
pipeline_defaults:
  tasks:
    - task: my_common_setup_task
      type: python
      image: myorg/myrepo:mypythonapp
      cmd: python -u my_setup_module.py
    - task: pipeline_tasks
      type: pipeline
    - task: my_common_teardown_task1
      type: python
      image: myorg/myrepo:mypythonapp
      cmd: python -u my_teardown_module1.py
    - task: my_common_teardown_task2
      type: python
      image: myorg/myrepo:mypythonapp
      cmd: python -u my_teardown_module2.py
```  

In the example above we set a list of `tasks` in `pipeline_defaults` which leads to each pipeline defined in our
liminal.yml file will have `my_common_setup_task` run before its tasks and
`my_common_teardown_task1` and `my_common_teardown_task2` after its tasks.

## Inheritence

Each liminal.yml defines a subliminal layer of a liminal system. A subliminal layer can inherit attributes of a
superliminal layer by specifying `super: name_of_super` in the root of the yml.

```yaml
name: my_system
super: my_super
```

A super is found by this name if a liminal.yml file in your environment exists with that name. A superliminal layer
liminal.yml file needs to define its `type` as `super`:

```yaml
name: my_super
type: super
```

If not specified, the `type` of a liminal.yml file defaults to `sub` (subliminal).

A superliminal can also inherit from another superliminal by defining its own `super` attribute.

```yaml
name: my_super
type: super
super: my_other_super
```

A liminal system can have 1 subliminal layer but many superliminal layers using inheritence. This allows us to chain
common behaviors of our systems into several superliminal layers.

If no `super` is defined for a liminal.yml file then it defaults to having the
[base](https://github.com/Natural-Intelligence/liminal/blob/master/liminal/core/config/defaults/base/liminal.yml)
be its super.

### superliminal attribtues

A superliminal layer can define the following attributes:

```
variables
executors
monitoring
task_defaults
pipeline_defaults
```

If the same attribute section is defined in both a superliminal and a lower layer of the system they will be merged,
with key collisions favoring the lower level layer.
