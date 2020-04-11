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
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

# Use an official Python runtime as a parent image
FROM python:3.7-slim

# Install aptitude build-essential
#RUN apt-get install -y --reinstall build-essential

# Set the working directory to /app
WORKDIR /app

# Order of operations is important here for docker's caching & incremental build performance.    !
# Be careful when changing this code.                                                            !

# Install any needed packages specified in python_server_requirements.txt and requirements.txt
COPY ./python_server_requirements.txt /app/
RUN pip install -r python_server_requirements.txt

COPY ./requirements.txt /app/
RUN {{mount}} pip install -r requirements.txt

# Copy the current directory contents into the container at /app
RUN echo "Copying source code.."
COPY . /app/

CMD python -u rainbow_python_server.py
