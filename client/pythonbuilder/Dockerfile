# syntax=docker/dockerfile:1
FROM python:3.10-bullseye as pythonbuilder
WORKDIR /builder
RUN apt-get update && apt-get apt-utils install build-essential clang -y
COPY . .
# install the modules as --user option allow a later copy
RUN python -m venv .venv
RUN .venv/bin/python -m pip install wheel
RUN .venv/bin/python -m pip install ./pyedge
RUN .venv/bin/python -m pip install -r requirements.txt
