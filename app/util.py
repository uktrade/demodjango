def render_connection_info(addon_type: str, success: bool, connection_info: str = False):
    output = (f'{addon_type}: '
              f'<span style="color: green">{"✓" if success else "✗"}</span> <br> '
              f'{f"<pre><code>{connection_info}</code></pre>" if connection_info else ""} <hr>')
    return output
