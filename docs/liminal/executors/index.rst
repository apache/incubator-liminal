.. Apchae Liminal documentation master file, created by
   sphinx-quickstart on Sun Nov 15 08:45:27 2020.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

..
   Licensed to the Apache Software Foundation (ASF) under one
   or more contributor license agreements.  See the NOTICE file
   distributed with this work for additional information
   regarding copyright ownership.  The ASF licenses this file
   to you under the Apache License, Version 2.0 (the
   "License"); you may not use this file except in compliance
   with the License.  You may obtain a copy of the License at
..

..  http://www.apache.org/licenses/LICENSE-2.0

..
   Unless required by applicable law or agreed to in writing,
   software distributed under the License is distributed on an
   "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
   KIND, either express or implied.  See the License for the
   specific language governing permissions and limitations
   under the License.
..

Executors
=========

Each ``task`` in your pipelines has a reference to an executor from the ``executors`` section of
your liminal.yml file. If not specified, the appropriate default executor for that task type is
used.

.. code-block:: yaml

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

..

In the example above we define an ``executor`` of type ``kubernetes`` with custom resources
configuration.

``executors`` is a section in the root of your liminal.yml file and is a list of ``executor`` s
defined by the following attributes:

executor attributes
'''''''''''''''''''

``executor``: name of your executor.

``type``: type of the executor. The current available image types are: ``kubernetes`` and ``emr``.

Different executor types support their own additional configuration.

executor types
''''''''''''''

.. toctree::
   :maxdepth: 1

   kubernetes
