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

# Tasks

`task` is the definition of a specific step in your pipeline, and is part of the `tasks` list
in your pipeline definition.

For fully detailed information on pipelines see: [pipelines](../pipelines.md).

```yaml
  - task: my_python_task
    image: myorg/myrepo:mypythonapp
    cmd: python -u my_module.py
    env_vars:
      env: {{env}}
      fizz: buzz
```

A `task` is defined by the following attributes:

## task attributes

`task`: name of your task (must be made of alphanumeric, dash and/or underscore characters only).

`type`: type of the task. Examples of available task types are: `python`
and more..

Different task types require their own additional configuration. For example, `python` task requires
`image` to be configured.

## task types

1. [python](python.md)
