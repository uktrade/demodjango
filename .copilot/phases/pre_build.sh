#!/usr/bin/env bash

# Exit early if something goes wrong
set -e

git config --global credential.UseHttpPath true

# Add commands below to run as part of the pre_build phase

poetry run pytest tests/app

GITMODULES_FILE="./.gitmodules"

sed -i 's|git@github.com:\(.*\)|https://github.com/\1|g' "$GITMODULES_FILE"
