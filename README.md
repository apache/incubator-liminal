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
        description: task with input from other task's output
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


# Installation
1. Install this package
```bash
   pip install git+https://github.com/Natural-Intelligence/rainbow.git@rainbow_local_mode
```
2. Optional: set RAINBOW_HOME to path of your choice (if not set, will default to ~/rainbow_home)
```bash
echo 'export RAINBOW_HOME=</path/to/some/folder>' >> ~/.bash_profile && source ~/.bash_profile
```

# Authoring pipelines

This involves at minimum creating a single file called rainbow.yml as in the example above.

If your pipeline requires custom python code to implement tasks, they should be organized 
[like this](https://github.com/Natural-Intelligence/rainbow/tree/master/tests/runners/airflow/rainbow)

If your pipeline  introduces imports of external packages which are not already a part 
of the rainbow framework (i.e. you had to pip install them yourself), you need to also provide 
a requirements.txt in the root of your project.

# Testing the pipeline locally

When your pipeline code is ready, you can test it by running it locally on your machine.

1. Deploy the pipeline:
```bash
cd </path/to/your/rainbow/code> 
rainbow deploy
```
2. Make sure you have docker running
3. Start the Server
```bash
rainbow start
```
4. Navigate to [http://localhost:8080/admin]
5. You should see your ![pipeline](https://raw.githubusercontent.com/Natural-Intelligence/rainbow/rainbow_local_mode/images/airflow.png")

### Running Tests (for contributors)
When doing local development and running Rainbow unit-tests, make sure to set RAINBOW_STAND_ALONE_MODE=True
