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

# python_server image

The `python_server` image builder packages your python code as a docker image which starts a web
server to serve your code via HTTP calls.

```yaml
  - image: myorg/myrepo:mypythonserver
    type: python_server
    source: relative/path/to/source
    endpoints:
      - endpoint: /myendpoint
        module: my_module
        function: my_function
      - endpoint: /myotherendpoint
        module: my_module2
        function: my_function2
```

## attributes

`image`: name of your image.

`source`: location of source files to include in the image, this can be a relative path within your
project, or even `.` which means the entire project should be packaged in the image.

`endpoint`: list of `endpoint`s to expose in the server.

## endpoint attributes

`endpoint`: path to your endpoint in the server.

`module`: module containing your user code.

`function`: name of the function within the module that should be called when handling this
endpoint. the function should expect a dictionary as an input (or None if no input) and should
return a string to return in the response to the HTTP call.
