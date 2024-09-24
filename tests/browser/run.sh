#!/bin/bash

target="$1"
tests="$2"
maintenace_page_bypass_value="$3"

case "${target}" in
  "" | "local")
    host="http://localhost:8080"
    ;;
  *.*)
    host="https://${target}/"
    export IS_CDN=True
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

if [ -n "$maintenace_page_bypass_value" ]; then
  export MAINTENANCE_PAGE_BYPASS_VALUE=${maintenace_page_bypass_value}
fi

poetry run pytest ./tests/browser/$tests
