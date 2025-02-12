from fastapi.responses import RedirectResponse
from starlette.middleware.base import BaseHTTPMiddleware

from .auth import keycloak_openid
from .encrypt import CookieEncrypter


class AuthorizationMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        user = None
        if request.url.path.startswith("/priv"):
            session_x = request.cookies.get("session-x")
            token = CookieEncrypter.decrypt(session_x)
            if not token:
                return RedirectResponse(url="/auth/login")
            try:
                user = keycloak_openid.userinfo(token)
            except Exception as e:
                return RedirectResponse(url="/auth/login")
        request.scope["user"] = user
        response = await call_next(request)
        return response