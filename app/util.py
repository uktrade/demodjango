import logging
from typing import Callable

from normality import slugify

logger = logging.getLogger("django")


STATUS_SUCCESS = "✓"
STATUS_FAIL = "✗"

def dummy():
    return "OK"
class Check:
    def __init__(self, type: str, description: str, function: Callable, optional: bool=False):
        self.type = type
        self.description = description
        self.function = function
        self.optional = optional

    def __call__(self):
        return self.function()


class CheckResult:
    def __init__(self, type: str, description: str, success: bool, message: str = "", check: Check=Check(None,None,dummy)):
        self.check = check
        self.type = type
        self.description = description
        self.success = success
        self.message = message

    def to_dict(self):
        return {
            "type": self.check.type or self.type,
            "description": self.check.description or self.description,
            "success": self.success,
            "message": self.message,
        }


def render_connection_info(check_result: CheckResult):
    log_detail_base = f"Rendering {check_result.description} stuff "
    if check_result.success:
        logger.info(f"{log_detail_base} successful")
        status_icon = STATUS_SUCCESS
        status_colour = "green"
    else:
        logger.error(f"{log_detail_base} failed with error: {check_result.message}")
        status_icon = STATUS_FAIL
        status_colour = "red"

    if check_result.message:
        page_detail = f"<pre><code style='white-space: pre-wrap'>{check_result.message}</code></pre>"
    else:
        page_detail = ""

    output = (
        f"<div>"
        f"{check_result.description}: "
        f'<span data-testid="{slugify(check_result.description)}" style="color: {status_colour}">'
        f"{status_icon}</span> <br> "
        f"{page_detail} <hr>"
        f"</div>"
    )

    return output
