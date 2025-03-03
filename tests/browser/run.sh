#!/bin/bash

target="$1"
tests="$2"
maintenace_page_bypass_value="$3"

case "${target}" in
  "" | "local")
    web_service_url="http://localhost:8080"
    # Todo: If we want to be able to test this locally via Docker Compose api_service_url="http://localhost:8080"
    ;;
  *)
    web_service_url="https://web.${target}.demodjango.uktrade.digital/"
    api_service_url="https://api.${target}.demodjango.uktrade.digital/"
    ;;
esac

echo -e "\nInstall playwright browsers and dependencies"
poetry run playwright install --with-deps

echo -e "\nRunning $tests tests against ${target} environment"
export WEB_SERVICE_URL=${web_service_url}
export API_SERVICE_URL=${api_service_url}

if [ -n "$maintenace_page_bypass_value" ]; then
  export MAINTENANCE_PAGE_BYPASS_VALUE=${maintenace_page_bypass_value}
fi

poetry run pytest ./tests/browser/$tests
