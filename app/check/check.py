from typing import Union, List

from app.check.report import CheckReport


class Check:
    def execute(self):
        raise NotImplemented

    @property
    def success(self) -> bool:
        raise NotImplemented

    @property
    def report(self) -> Union[CheckReport, List[CheckReport]]:
        raise NotImplemented
