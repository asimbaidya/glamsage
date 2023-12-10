from functools import wraps
from urllib.parse import urlparse

from flask import redirect, render_template, request, url_for


def redirect_if_not_htmx(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        # in order for this to work, every htmx-request must add this header when making a request
        if not request.headers.get("Hx-Request"):
            parsed_url = urlparse(request.url)

            # logs
            print(
                f"⏩`{parsed_url.geturl()}` is not requested by htmx. ⏩ Redirecting..."
            )
            return render_template("layout.html", next=parsed_url.geturl())
        return func(*args, **kwargs)

    return wrapper
