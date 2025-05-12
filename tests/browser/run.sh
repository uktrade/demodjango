#!/bin/bash

target="$1"
tests="$2"
maintenance_page_bypass_value="$3"

case "${target}" in
  "" | "local")
    web_service_url="http://localhost:8080"
    # Todo: If we want to be able to test this locally via Docker Compose api_service_url="http://localhost:8080"
     ;;
  "prod")
    web_service_url="https://web.demodjango.prod.uktrade.digital/"
    api_service_url="https://api.demodjango.prod.uktrade.digital/"
    ip_filter_test_service_url="https://ip-filter-test.demodjango.prod.uktrade.digital/"
    ;;
  "prode2e")
    web_service_url="https://web.prode2e.demodjango.prod.uktrade.digital/"
    api_service_url="https://api.prode2e.demodjango.prod.uktrade.digital/"
    ip_filter_test_service_url="https://ip-filter-test.prode2e.demodjango.prod.uktrade.digital/"
    ;;
  *)
    web_service_url="https://web.${target}.demodjango.uktrade.digital/"
    api_service_url="https://api.${target}.demodjango.uktrade.digital/"
    ip_filter_test_service_url="https://ip-filter-test.${target}.demodjango.uktrade.digital/"
    ;;
esac

echo -e "\nInstalling Playwright browsers and dependencies..."
poetry run playwright install --with-deps

echo -e "\nRunning $tests tests against the ${target} environment..."
export WEB_SERVICE_URL=${web_service_url}
export API_SERVICE_URL=${api_service_url}
export IP_FILTER_TEST_SERVICE_URL=${ip_filter_test_service_url}

if [ -n "$maintenance_page_bypass_value" ]; then
  export MAINTENANCE_PAGE_BYPASS_VALUE=${maintenance_page_bypass_value}
fi

poetry run pytest ./tests/browser/$tests
