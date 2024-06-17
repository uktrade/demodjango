#!/bin/bash

target="$1"

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

echo -e "\nRunning smoke tests against ${host}"

export LANDING_PAGE_URL=${host}
poetry run pytest ./tests/smoke
