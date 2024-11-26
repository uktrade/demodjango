import logging

from normality import slugify

logger = logging.getLogger("django")


STATUS_SUCCESS = "✓"
STATUS_FAIL = "✗"


def render_connection_info(
    addon_type: str, success: bool, connection_info: str = False
):
    log_detail_base = f"Rendering {addon_type} stuff "
    if success:
        logger.info(f"{log_detail_base} successful")
        status_icon = STATUS_SUCCESS
        status_colour = "green"
    else:
        logger.error(f"{log_detail_base} failed with error: {connection_info}")
        status_icon = STATUS_FAIL
        status_colour = "red"

    if connection_info:
        page_detail = (
            f"<pre><code style='white-space: pre-wrap'>{connection_info}</code></pre>"
        )
    else:
        page_detail = ""

    output = (
        f"<div>"
        f"{addon_type}: "
        f'<span data-testid="{slugify(addon_type)}" style="color: {status_colour}">'
        f"{status_icon}</span> <br> "
        f"{page_detail} <hr>"
        f"</div>"
    )

    return output


def check_results_as_dict(addon_type: str, success: bool, connection_info: str = ""):
    return {"check": addon_type, "success": success, "info": connection_info}
