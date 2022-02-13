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

# python task

The `python` task allows you to run python code packaged as docker images.

```yaml
  - task: my_python_task
    type: python
    image: myorg/myrepo:mypythonapp
    cmd: python my_python_app.py
    env_vars:
      env: '{{env}}'
      fizz: buzz
    mounts:
      - mount: mymount
        volume: myvol1
        path: /mnt/vol1
```

## attributes

`task`: name of your task (must be made of alphanumeric, dash and/or underscore characters only).

`image`: name of image to run.

`cmd`: command to run when running the image.

`env_vars`: environment variables to set when running the image.

`mounts`: list of `mount`s defined by the following attributes:

### mount attributes

`mount`: name of the mount.

`volume`: volume to mount. volumes are defined in the `volumes` section of liminal.yml

`path`: path in which to mount the volume. this is the path accessible to user code.
