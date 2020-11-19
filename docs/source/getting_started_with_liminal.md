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

# Getting Started with Apache Liminal

Liminal is a data systems orchestration platform. Liminal enables data scientists and data engineers to define their data systems and flow using configuration.
From feature engineering to production monitoring - and the framework takes care of the infra behind the scenes and seamlessly integrates with the infrastructure behind the scenes.


## Quick Start

This guide will allow you to set up your first apache Liminal environment and allow you to create some simple ML pipelines. These will be very similar to the ones you are going to build for real production scenarios. This is actually the magic behind Liminal.

## Prerequisites

Python 3 (3.6 and up)

[Docker Desktop](https://www.docker.com/products/docker-desktop)

*Note: Make sure kubernetes cluster is running in docker desktop (or custom kubernetes installation on your machine).*

### Apache Liminal Hello World

In this tutorial, we will go through setting up Liminal for the first time on your local dev machine.

I’m running this on my macBook, so this will cover mac related installation aspects and kinks (if there are any).

First, let’s build our examples project:

In the dev folder, just clone the example code from liminal:


```
git clone https://github.com/apache/incubator-liminal
```
***Note:*** *You just cloned the entire Liminal Project, you actually need just the examples folder.*

Create a python virtualenv to isolate your runs, like this:

```
cd incubator-liminal/examples/liminal-getting-started
python3 -m venv env
```

And activate your virtual environment:

```
source env/bin/activate
```

Now we are ready to install liminal:

```
pip install apache-liminal
rm -rf ~/liminal_home
```
Let's build the images you need for the example:
```
liminal build
```
The build will create docker images based on the Liminal.yml file, each task and service will have its docker image created.

```
liminal deploy --clean  
```
The deploy will create missing containers from the images created above as well as basic Apache AirFlow containers needed to run the pipelines, and deploy them to your local docker (docker-compose)

*Note: Liminal creates a bunch of assets, some are going to be located under: the directory in your LIMINAL_HOME env variable. But default LIMINAL_HOME is set to ~/liminal_home directory.*

*Note: the --clean flag is for removing old containers from the previous installs, it will not remove old images.*

Now lets runs it:
```
liminal start
```
Liminal now spins up the Apache AirFlow containers it will run the dag created based on the Liminal.yml file.
It includes these three containers: 
* liminal-postgress
* liminal-webserver
* liminal-scheduler

Once it finished loading the, 
Go to the Apache AirFlow admin in the browser:


```
http://localhost:8080/admin
```
You can just click: [http://localhost:8080/admin](http://localhost:8080/admin)


![](nstatic/airflow_main.png)

***Important:** Click on the “On” button to activate the dag, nothing will happen otherwise!*

You can go to tree view to see all the tasks configured in the liminal.yml file: \
[http://localhost:8080/admin/Apache AirFlow/tree?dag_id=example_pipeline](http://localhost:8080/admin/Apache AirFlow/tree?dag_id=example_pipeline)

Now lets see what actually happened to our task:

![](nstatic/airflow_view_dag.png)

Click on “hello_world_example” and you will get this popup: \

![](nstatic/airflow_view_log.png) \
Click on “view log” button and you can see the log of the current task run: \


![](nstatic/airflow_task_log.png)

### mounted volumes
All Tasks use a mounted volume as defined in the pipeline YAML:
```YAML
name: GettingStartedPipeline
volumes:
  - volume: gettingstartedvol
    local:
      path: ./
```
In our case the mounted volume will point to the liminal hello world example.
The hello world task will read the **hello_world.json** file from the mounted volume and will write the **hello_world_output.json** to it.

*Note:* Each task will internally mount the volume defined above to an internal representation, described under the task section in the yml:

```YAML
  task:
  ...
  mounts:
     - mount: taskmount
       volume: gettingstartedvol
       path: /mnt/vol1
```

### Here are the entire list of commands, if you want to start from scratch:

```
git clone https://github.com/apache/incubator-liminal
cd examples
python3 -m venv env
source env/bin/activate
pip uninstall apache-liminal
pip install apache-liminal
rm -rf ~/liminal_home
Liminal build
liminal deploy --clean
liminal start
```

### Closing up

Making sure the airflow containers are closed, just click:

```
liminal stop
```

Or you can do it manually, stop the running containers:
```
docker container stop liminal-postgress  liminal-webserver liminal-scheduler```
```

And don't forget to deactivate the python virtualenv, just write:

```
deactivate
```
