import json
from typing import Any, Dict
from django.http import JsonResponse, HttpRequest
from crm.services.errors import BadRequest, Forbidden, NotFound, CrmError

def json_body(request: HttpRequest) -> Dict[str, Any]:
    try:
        raw = request.body.decode("utf-8") if request.body else "{}"
        return json.loads(raw or "{}")
    except Exception:
        raise BadRequest("Invalid JSON body")

def ok(data: Any = None, status: int = 200):
    return JsonResponse({"ok": True, "data": data}, status=status)

def fail(message: str, status: int):
    return JsonResponse({"ok": False, "error": message}, status=status)

def handle_service_errors(fn):
    def wrapper(request: HttpRequest, *args, **kwargs):
        try:
            return fn(request, *args, **kwargs)
        except BadRequest as e:
            return fail(str(e), 400)
        except Forbidden as e:
            return fail(str(e), 403)
        except NotFound as e:
            return fail(str(e), 404)
        except CrmError as e:
            return fail(str(e), 500)
    return wrapper
