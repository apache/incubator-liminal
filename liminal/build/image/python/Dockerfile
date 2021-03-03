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

# Update apt
RUN echo "Updating apt"
RUN apt-get update --fix-missing

# Install gcc
RUN echo "Installing gcc"
RUN apt-get install -y gcc

# Install git
RUN echo "Installing git"
RUN apt-get install -y git
ARG GIT_USER=no_user_supplied
ARG GIT_PASSWORD=""
ARG GIT_AUTH=$GIT_USER":"$GIT_PASSWORD

# Install any needed packages specified in requirements.txt
COPY ./requirements.txt /app/
{{copy_pip_conf}}

# mount the secret in the correct location, then run pip install
RUN pip install --upgrade pip
RUN {{mount}} pip install -r requirements.txt

# Install pipenv
RUN echo "Installing pipenv.."
RUN pip install pipenv

# Install awscli
RUN echo "Installing awscli.."
RUN pipenv install awscli

# Copy the current directory contents into the container at /app
RUN echo "Copying source code.."
COPY . /app/
