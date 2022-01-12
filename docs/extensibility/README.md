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

# Extensibility

The extensibility designed to have an easy way for the users to add their tasks, executors, image
builders and extend the library so that it fits the level of abstraction that suits the user
environment.

## Location

Tasks folder: `{LIMINAL_HOME}/plugins/tasks`

Executors folder: `{LIMINAL_HOME}/plugins/executors`

Image builders folder: `{LIMINAL_HOME}/plugins/images`

## Example

### Prerequisites

Apache Liminal

### Guide

Check out the examples for each one of the extensible item
in [examples/extensibility](../../examples/extensibility)

Copy the extensible items to the plugin location:

```shell
cp -r ../../examples/extensibility/executors/* $LIMINAL_HOME/liminal/plugins/executors/
```

```shell
cp -r ../../examples/extensibility/tasks/* $LIMINAL_HOME/liminal/plugins/tasks/
```

```shell
cp -r ../../examples/extensibility/images/* $LIMINAL_HOME/liminal/plugins/images/
```

```shell
liminal build . 
liminal deploy --clean 
liminal start
```
