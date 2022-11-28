FROM python:3.8.2-slim-buster
MAINTAINER Sharath Addula
# install os-level dependencies
RUN apt-get update -y \
    && pip install --upgrade pip \
    && apt-get install -y apt-utils jq postgresql-client postgresql-contrib libpq-dev libmagic1 \
    && apt-get install -y apt-utils gnupg2 curl gcc vim zip alien

# Create the OS user; set directory permissions

ENV APP_PATH=/wmxapp

COPY . $APP_PATH

ENV PYTHONPATH=$APP_PATH
ENV WMX_HOME=$APP_PATH
ENV WAPI_KEY={api_key}

# Change the working directory
WORKDIR $APP_PATH

RUN pip install -r requirements.txt
