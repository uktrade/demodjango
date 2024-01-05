import logging


def render_connection_info(addon_type: str, success: bool, connection_info: str = False):
    log_detail = "successful" if success else f"failed with error: {connection_info}"
    # Todo: Log error if it's failed...
    logging.getLogger("django").info(f"Rendering {addon_type} stuff {log_detail}")
    page_detail = f"<pre><code style='white-space: pre-wrap'>{connection_info}</code></pre>" if connection_info else ""
    output = (f'{addon_type}: '
              f'<span style="color: {"green" if success else "red"}">'
              f'{"✓" if success else "✗"}</span> <br> '
              f'{page_detail} <hr>')
    return output
