def identity_context(request):
    ident = getattr(request, "identity", None)
    return {"request_identity": ident}
