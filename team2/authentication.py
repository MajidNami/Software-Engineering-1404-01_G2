from rest_framework.authentication import BaseAuthentication


class JWTMiddlewareAuthentication(BaseAuthentication):
    def authenticate(self, request):
        user = getattr(request._request, 'user', None)
        if user and user.is_authenticated:
            return (user, None)
        return None
