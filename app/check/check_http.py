from typing import List
from typing import Union
from urllib.parse import ParseResult
from urllib.parse import urlparse

import requests

from app.check.check import Check
from app.check.report import CheckReport


class HTTPCheckInstance:
    definition: str
    method: str
    url: ParseResult
    status_code: int
    report: CheckReport

    def __init__(self, definition: str):
        self.definition = definition
        self.report = CheckReport()
        self.report.summary = definition

    def execute(self):
        segments = self.definition.split("|")

        self.status_code = 200
        self.method = "get"

        self.url = urlparse(segments[0])

        try:
            status = segments[1]
            self.status_code = int(status)
        except IndexError:
            pass
        except ValueError:
            self.report.success = False
            self.report.errors.append(
                f"expected status code to be integer, got {segments[1]}"
            )
            return

        try:
            method = segments[2]
            self.method = method.lower()
        except IndexError:
            pass

        requester = getattr(requests, self.method, None)

        if not requester:
            self.report.success = False
            self.report.errors.append(
                f'method "{self.method.upper()}" is not a valid HTTP method'
            )
            return

        try:
            r = requester(self.url.geturl())

            if r.status_code != self.status_code:
                self.report.success = False
                self.report.errors.append(
                    f"expected HTTP Status {self.status_code} but got {r.status_code}"
                )

        except ValueError:
            self.report.success = False
            self.report.errors.append(f'"{self.url.geturl()}" is not a valid URL')
        except Exception as e:
            self.report.success = False
            self.report.errors.append(str(e))


class HTTPCheck(Check):
    checks: List[HTTPCheckInstance]

    def __init__(self, definition: str):
        self.checks = [HTTPCheckInstance(d) for d in definition.split(",")]

    def execute(self):
        for check in self.checks:
            check.execute()

    @property
    def success(self) -> bool:
        return all([c.report.success for c in self.checks])

    @property
    def report(self) -> Union[CheckReport, List[CheckReport]]:
        return [c.report for c in self.checks]
