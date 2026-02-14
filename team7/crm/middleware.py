from dataclasses import dataclass
from typing import Optional
from django.utils.deprecation import MiddlewareMixin

@dataclass(frozen=True)
class RequestIdentity:
    user_id: Optional[str] = None
    username: Optional[str] = None
    moderator_id: Optional[str] = None

class RequestIdentityMiddleware(MiddlewareMixin):
    """Extract lightweight identity headers for this microservice.

    This service is not an auth provider; it expects upstream identity. UI passes IDs in URL,
    but APIs can also send:
      - X-User-Id
      - X-Username (optional)
      - X-Moderator-Id (optional)
    """

    def process_request(self, request):
        request.identity = RequestIdentity(
            user_id=request.headers.get("X-User-Id"),
            username=request.headers.get("X-Username"),
            moderator_id=request.headers.get("X-Moderator-Id"),
        )
