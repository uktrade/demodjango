import logging
from typing import Callable

from normality import slugify

logger = logging.getLogger("django")


STATUS_SUCCESS = "✓"
STATUS_FAIL = "✗"


class Check:
    def __init__(self, test_id: str, description: str, optional: bool=False):
        self.test_id = test_id
        self.description = description
        self.optional = optional

    def __call__(self):
        raise NotImplementedError("Call function needs to be implemented in the subclass")

class CheckResult:
    def __init__(self, test_id: str, description: str, success: bool, message: str = ""):
        self.test_id = test_id
        self.description = description
        self.success = success
        self.message = message

    def to_dict(self):
        return {
            "test_id": self.test_id,
            "description": self.description,
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
