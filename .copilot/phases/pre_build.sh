#!/usr/bin/env bash

# Exit early if something goes wrong
set -e

# git config --global credential.UseHttpPath true

# Add commands below to run as part of the pre_build phase

# poetry run pytest tests/app

GITMODULES_FILE="./.gitmodules"

sed -i 's|git@github.com:\(.*\)|https://github.com/\1|g' "$GITMODULES_FILE"

# git_clone_base_url="https://codestar-connections.eu-west-2.amazonaws.com/git-http/563763463626/eu-west-2/122da7c9-9fa3-42b2-9125-1db0f957913d/uktrade"

# git config --global credential.helper '!aws codecommit credential-helper $@'
# git config --global credential.UseHttpPath true

# cat <<EOF > ./.gitmodules
# [submodule "demodjango-private"]
# 	path = demodjango-private
# 	url = $git_clone_base_url/demodjango-private.git
# EOF

git submodule update --init --remote --recursive
