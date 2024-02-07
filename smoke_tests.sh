#!/bin/bash

target="$1"

case "${target}" in
  "" | "local")
    host="http://localhost:8080"
    ;;
  *)
    host="https://v2.demodjango.${target}.uktrade.digital/"
    ;;
esac

echo "Running smoke tests against ${target}"

export LANDING_PAGE_URL=${host}
pytest ./tests/smoke
