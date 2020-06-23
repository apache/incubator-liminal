#!/bin/bash
#
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required bgit y applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

echo $1
target_path="$1"

echo "running from " $(PWD)
echo "target path for liminal zip file is " $target_path

echo "cleaning up the temp dirs $TMPDIR/liminal_build"
rm -rf $TMPDIR/liminal_build-*/

tmp_dir=$(mktemp -d -t liminal_build-)
echo "creating temp directory $tmp_dir"

docker_build_dir=$tmp_dir/docker_build
mkdir -p $docker_build_dir
echo "docker build directory :"$docker_build_dir

mkdir $docker_build_dir/"zip_content"
mkdir $docker_build_dir/"dags"

#copy the content of the user project into the build folder
rsync -a --exclude 'venv' $(PWD)/ $docker_build_dir/zip_content/

# perform installation of external pacakges (framework-requirements and user-requirements)
# this is done inside a docker to 1) avoid requiring the user to install stuff, and 2) to create a platform-compatible
# package (install the native libraries in a flavour suitable for the docker in which airflow runs, and not user machine)

docker run --rm --name liminal_build -v /private/"$docker_build_dir":/home/liminal/tmp --entrypoint="" -u 0 \
       puckel/docker-airflow:1.10.9 /bin/bash -c "cd /home/liminal/tmp/zip_content &&
       pip install --no-deps --target=\"/home/liminal/tmp/zip_content\" liminal==0.0.2dev5 &&
       rsync -avzh --ignore-errors /home/liminal/tmp/zip_content/liminal-resources/* /home/liminal/tmp/zip_content/
       pip install --target=\"/home/liminal/tmp/zip_content\" -r /home/liminal/tmp/zip_content/requirements-airflow.txt &&
       pip install --target=\"/home/liminal/tmp/zip_content\" -r /home/liminal/tmp/zip_content/requirements.txt"


# zip the content per https://airflow.apache.org/docs/stable/concepts.html#packaged-dags
cd $docker_build_dir/zip_content
mv docker-compose.yml $target_path
rm __init__.py

zip -r ../dags/liminal.zip .
cp ../dags/liminal.zip $target_path
