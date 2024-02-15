from typing import List

import jinja2


class CheckReport:
    success: bool
    summary: str
    errors: List[str]

    def __init__(self, success: bool = True, summary: str = '', errors: List[str] = None) -> None:
        self.success = success
        self.summary = summary
        self.errors = errors if errors else []

    def render(self) -> str:
        env = jinja2.Environment(loader=jinja2.FileSystemLoader("app/views"),
                                 keep_trailing_newline=True)

        report_template = env.get_template('report.html')

        return report_template.render({'report': self})
