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

# delete_cloudformation_stack task

The `delete_cloudformation_stack` task allows you to delete stack

```yaml
    - task: delete_emr
      type: delete_cloudformation_stack
      stack_name: liminal_emr_stack_name
      description: delete stack
```

## attributes

`task`: name of your task (must be made of alphanumeric, dash and/or underscore characters only).

`stack_name`: the name of the stack to delete
