# app/utils/common.py

import datetime as dt


def ensure_aware(d: dt.datetime) -> dt.datetime:
    """Return UTC-aware datetime."""
    if d.tzinfo is None:
        return d.replace(tzinfo=dt.timezone.utc)
    return d.astimezone(dt.timezone.utc)


def now_utc() -> dt.datetime:
    """Current UTC now (timezone aware)."""
    return dt.datetime.now(dt.timezone.utc)
