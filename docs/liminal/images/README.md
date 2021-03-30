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

# Images

In the `images` section you can configure how to pack your code into docker images. This can be
achieved in liminal easily, without any Docker knowledge needed by setting just a few attributes:

```yaml
images:
  - image: myorg/myrepo:mypythonapp
    type: python
    source: .
  - image: myorg/myrepo:myserver
    type: python_server
    source: path/to/my/server/code 
    endpoints:
      - endpoint: /myendpoint
        module: my_module
```

`images` is a section in the root lof your liminal.yml file and is a list of `image`s, defined 
by the following attributes:

## image attributes

`image`: name of your image, usually will be in the form of `user/repository:tag` common in docker
image repositories such as Docker Hub, but for local development this can be any string.

`type`: type of the image. Usually this will match your coding language, or your coding langauge
followed by an `_` and a specific style of application (such as a server).

`source`: location of source files to include in the image, this can be a relative path within your
project, or even `.` which means the entire project should be packaged in the image.

`build_cmd`: certain languages require to be built or compiled, here you can provide your build
command to be executed in order to build your code.

Other image types might require additional configuration, for example, servers require `endpoints`
to be configured.

## image types

1. [python](python.md)
2. [python server](python_server.md)
