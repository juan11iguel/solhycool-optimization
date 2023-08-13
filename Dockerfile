FROM python:3.11.2-bullseye
LABEL maintainer="Juan Miguel Serrano Rodríguez (jmserrano@psa.es)"

# Install micro editor
RUN apt-get update
RUN apt-get install -y xclip micro
RUN apt-get install -y nano

# Create project directory
RUN mkdir -p /wascop_app/
# Upgrade pip
RUN pip install --upgrade pip

# Install python dependencies
COPY requirements.txt /wascop_app/requirements.txt
RUN pip install -r /wascop_app/requirements.txt

# Copy project files
COPY . /wascop_app
