# Use an official Python runtime as a parent image
FROM python:3.7-slim

# Install aptitude build-essential
#RUN apt-get install -y --reinstall build-essential

# Set the working directory to /app
WORKDIR /app

# Order of operations is important here for docker's caching & incremental build performance.    !
# Be careful when changing this code.                                                            !

# Install any needed packages specified in python_server_requirements.txt and requirements.txt
COPY ./python_server_requirements.txt /app
RUN pip install -r python_server_requirements.txt

COPY ./requirements.txt /app
RUN pip install -r requirements.txt

# Copy the current directory contents into the container at /app
RUN echo "Copying source code.."
COPY . /app

CMD python -u rainbow_python_server.py
