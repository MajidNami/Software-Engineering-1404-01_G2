"""
Lightweight JWT authentication middleware for team11 microservice.

Decodes JWT tokens issued by the core auth service and sets
request.jwt_user_id so views can identify the logged-in user
without depending on the core Django app or its User model.
"""

import jwt
from django.conf import settings
from django.utils.deprecation import MiddlewareMixin


class JWTAuthMiddleware(MiddlewareMixin):
    """
    Reads access_token from cookie (or Authorization: Bearer header),
    decodes it with the shared JWT_SECRET, and sets:
        request.jwt_user_id  – int | None
        request.jwt_payload  – dict | None
    """

    def process_request(self, request):
        request.jwt_user_id = None
        request.jwt_payload = None

        # 1. Try cookie first, then Authorization header
        token = request.COOKIES.get("access_token")
        if not token:
            auth = request.headers.get("Authorization", "")
            if auth.startswith("Bearer "):
                token = auth.split(" ", 1)[1].strip()

        if not token:
            return

        # 2. Decode & validate
        try:
            payload = jwt.decode(
                token,
                settings.JWT_SECRET,
                algorithms=[settings.JWT_ALGORITHM],
            )

            if payload.get("type") != "access":
                return

            user_id = payload.get("sub")
            if user_id is not None:
                request.jwt_user_id = user_id
                request.jwt_payload = payload

        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
            # Invalid / expired token → treat as unauthenticated
            return
