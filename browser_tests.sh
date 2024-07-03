#!/bin/bash

target="$1"
tests="$2"

case "${target}" in
  "" | "local")
    host="http://localhost:8080"
    ;;
  *)
    host="https://internal.${target}.demodjango.uktrade.digital/"
    ;;
esac

echo -e "\nInstalling required browsers"
poetry run playwright install
poetry run playwright install-deps

echo -e "\nRunning $tests tests against ${host}"
export LANDING_PAGE_URL=${host}
poetry run pytest ./tests/$tests
