from fastapi import Request, Cookie
from fastapi.responses import RedirectResponse


def authentication_required():
    def inner(func):
        def wrapper(request: Request, authenticated=Cookie(default=False)):
            if bool(authenticated):
                return func(request=request)
            else:
                return RedirectResponse(url=request.url_for("admin_login"), status_code=303)

        return wrapper

    return inner
