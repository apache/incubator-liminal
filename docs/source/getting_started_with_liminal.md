

# Getting Started with Apache Liminal

Liminal is a data systems orchestration platform. Liminal enables data scientists and data engineers to define their data systems and flow using configuration.
From feature engineering to production monitoring - and the framework takes care of the infra behind the scenes and seamlessly integrates with the infrastructure behind the scenes.



## Quick Start

So, you’ve heard about liminal and decided you want to give it a try.

This guide will allow you to set up your first apache Liminal environment and allow you to create some simple ML pipelines. These will be very similar to the ones you are going to build for real production scenarios. This is actually the magic behind Liminal.



## Prerequisites

Python 3 (3.6 and up)

[Docker Desktop](https://www.docker.com/products/docker-desktop)

*Note: make sure your kubernetes cluster is running*

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
source ../env/bin/activate
```

Now we are ready to install liminal:


```
pip uninstall apache-liminal 
pip install apache-liminal
rm -rf ~/liminal_home
```
Let's build the images you need for the example:
```
liminal build
```
The build will create docker images based on the Liminal.yml file, eash task and service will have its docker image created.


```
liminal deploy --clean  # the --clean is for removing old containers from the previous install
```
The deploy will create missing containers from the images created above as well as basic Airflow containers needed to run the piplines, and deploy them to your local kubernetes cluster

*Note: Liminal creates a bunch of assets, some are going to be located under: the directory in your LIMINAL_HOME env variable. But default LIMINAL_HOME is set to ~/liminal_home directory.*

Now lets runs it:
```
liminal start
```
Liminal now spins up the AirFlow containers it will run the dag created based on the Liminal.yml file.
It includes these three containers: 
* liminal-postgress
* liminal-webserver
* liminal-scheduler

Once it finished loading the, 
Go to the airflow admin in the browser:


```
http://localhost:8080/admin
```
You can just click: [http://localhost:8080/admin](http://localhost:8080/admin)


![drawing](nstatic/airflow_main.png)

***Important:** Click on the “On” button to activate the dag, nothing will happen otherwise!*

You can go to tree view to see all the tasks configured in the liminal.yml file: \
[http://localhost:8080/admin/airflow/tree?dag_id=example_pipeline](http://localhost:8080/admin/airflow/tree?dag_id=example_pipeline)

Now lets see what actually happened to our task:

![drawing](nstatic/airflow_view_dag.png)

Click on “hello_world_example” and you will get this popup: \

![drawing](nstatic/airflow_view_log.png) \
Click on “view log” button and you can see the log of the current task run: \


![drawing](nstatic/airflow_task_log.png)

And That's it!

### Here are the entire list of commands, if you want to start from scratch:

```
git clone https://github.com/amihayz/liminal-examples
cd liminal-examples
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

Killing (cmd-c) the cmd you are running in would partially stop the containers in Docker desktop.
But, for making sure the dockers have closed:


```
docker container stop liminal-postgress
docker container stop liminal-webserver
docker container stop liminal-scheduler
```


And don't forget to stop the python virtualenv, just write:


```
deactivate
```
