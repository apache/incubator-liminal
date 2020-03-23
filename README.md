# Rainbow

Rainbow is an end-to-end platform for data engineers & scientists, allowing them to build,
train and deploy machine learning models in a robust and agile way.

The platform provides the abstractions and declarative capabilities for
data extraction & feature engineering followed by model training and serving.
Rainbow's goal is to operationalize the machine learning process, allowing data scientists to
quickly transition from a successful experiment to an automated pipeline of model training,
validation, deployment and inference in production, freeing them from engineering and
non-functional tasks, and allowing them to focus on machine learning code and artifacts.

# Basics

Using simple YAML configuration, create your own schedule data pipelines (a sequence of tasks to
perform), application servers,  and more.

## Example YAML config file
```yaml
name: MyPipeline
owner: Bosco Albert Baracus
pipelines:
  - pipeline: my_pipeline
    start_date: 1970-01-01
    timeout_minutes: 45
    schedule: 0 * 1 * *
    metrics:
     namespace: TestNamespace
     backends: [ 'cloudwatch' ]
    tasks:
      - task: my_static_input_task
        type: python
        description: static input task
        image: my_static_input_task_image
        source: helloworld
        env_vars:
          env1: "a"
          env2: "b"
        input_type: static
        input_path: '[ { "foo": "bar" }, { "foo": "baz" } ]'
        output_path: /output.json
        cmd: python -u hello_world.py
      - task: my_parallelized_static_input_task
        type: python
        description: parallelized static input task
        image: my_static_input_task_image
        env_vars:
          env1: "a"
          env2: "b"
        input_type: static
        input_path: '[ { "foo": "bar" }, { "foo": "baz" } ]'
        split_input: True
        executors: 2
        cmd: python -u helloworld.py
      - task: my_task_output_input_task
        type: python
        description: parallelized static input task
        image: my_task_output_input_task_image
        source: helloworld
        env_vars:
          env1: "a"
          env2: "b"
        input_type: task
        input_path: my_static_input_task
        cmd: python -u hello_world.py
services:
  - service:
    name: my_python_server
    type: python_server
    description: my python server
    image: my_server_image
    source: myserver
    endpoints:
      - endpoint: /myendpoint1
        module: myserver.my_server
        function: myendpoint1func
```

## Example repository structure
[Example repository structure](https://github.com/Natural-Intelligence/rainbow/tree/master/tests/runners/airflow/rainbow])
# Installation

TODO: installation.
