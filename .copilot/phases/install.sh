#!/usr/bin/env bash

# Exit early if something goes wrong
set -e

# Add commands below to run as part of the install phase

pip install poetry
poetry install
