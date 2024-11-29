import json
import os
import urllib.request
from http import HTTPStatus


def test_page_loads_with_title_and_has_success_ticks():
    url = os.getenv("WEB_SERVICE_URL") or "http://localhost:8080/" + "?json=true"
    with urllib.request.urlopen(url) as response:
        data = json.loads(response.read())

        assert response.status == HTTPStatus.OK
        results = data["check_results"]
        for result in results:
            check_success = "OK" if result["success"] else "FAIL"
            failure_message = "" if result["success"] else f" ({result['message']})"
            print(f"{result['type']}: {check_success}{failure_message}")

        assert all([result["success"] for result in results])
