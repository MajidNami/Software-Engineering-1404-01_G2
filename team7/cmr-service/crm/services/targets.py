from .identity import ensure_target

def get_target_name(target_id: str) -> str:
    target = ensure_target(target_id)
    return target.target_name or ""
