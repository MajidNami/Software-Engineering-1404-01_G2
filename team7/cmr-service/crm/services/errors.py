class CrmError(Exception):
    pass

class BadRequest(CrmError):
    pass

class Forbidden(CrmError):
    pass

class NotFound(CrmError):
    pass
