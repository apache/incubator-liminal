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

Metrics Backends
================

``metrics_backend`` is the definition of a metrics backend to which all automatically
generated metrics from your pipeline are sent to and is part of the ``metrics_backends`` list in the
``monitoring`` section of your liminal.yml

.. code-block:: yaml

  - metrics_backend: cloudwatch_metrics
    type: aws_cloudwatch
    namespace: DataPipeline
    AWS_REGION_NAME: us-east-1

..

A ``metrics_backend`` is defined by the following attributes:

metrics_backend attributes
''''''''''''''''''''''''''

``metrics_backend``: name of your metrics backend

``type``: type of the metrics backend. The current available metrics backends are: ``aws_cloudwatch``.

Different metrics backend types require their own additional configuration. For example,
``aws_cloudwatch`` metrics backend requires ``namespace`` to be configured.

metrics_backend types
'''''''''''''''''''''

.. toctree::
   :maxdepth: 1

   aws_cloudwatch
