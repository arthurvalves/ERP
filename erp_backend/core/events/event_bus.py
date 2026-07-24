from typing import Callable, Dict, List

_handlers: Dict[str, List[Callable]] = {}

def subscribe(event_name: str, handler: Callable):
    _handlers.setdefault(event_name, []).append(handler)

def emit(event_name: str, payload: dict):
    handlers = _handlers.get(event_name, [])
    for h in handlers:
        try:
            h(payload)
        except Exception:
            # handlers must be resilient; swallow exceptions to avoid breaking flow
            pass
