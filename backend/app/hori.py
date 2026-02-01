# app/hori.py
import datetime as dt
import os
from typing import List, Tuple, Optional
import httpx
from .models import SegmentPoint, HoriSegment, HoriSummary


# ---- UTC helpers ----
def ensure_aware(d: dt.datetime) -> dt.datetime:
    if d.tzinfo is None:
        return d.replace(tzinfo=dt.timezone.utc)
    return d.astimezone(dt.timezone.utc)


def _iso(ts: dt.datetime) -> str:
    ts = ensure_aware(ts)
    return ts.replace(microsecond=0).isoformat().replace("+00:00", "Z")


def parse_iso(ts: str) -> dt.datetime:
    """Always return timezone-aware UTC datetime."""
    try:
        d = dt.datetime.fromisoformat(ts.replace("Z", "+00:00"))
    except:
        return dt.datetime.now(dt.timezone.utc)

    return ensure_aware(d)


# ---- Forecast Helpers ----
def _closest_hour_idx(times: list[str], target: dt.datetime) -> Optional[int]:
    target = ensure_aware(target)
    parsed = []

    for t in times:
        try:
            d = dt.datetime.fromisoformat(t.replace("Z", "+00:00"))
            parsed.append(ensure_aware(d))
        except:
            continue

    if not parsed:
        return None

    return min(range(len(parsed)), key=lambda i: abs(parsed[i] - target))


async def _fetch_temp_once(lat: float, lon: float, at: dt.datetime) -> float:
    at = ensure_aware(at)

    url = (
        "https://api.open-meteo.com/v1/forecast"
        f"?latitude={lat}&longitude={lon}&hourly=temperature_2m&timezone=UTC"
    )

    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.get(url)
        r.raise_for_status()
        h = r.json().get("hourly", {})

    times = h.get("time", [])
    temps = h.get("temperature_2m", [])

    idx = _closest_hour_idx(times, at)
    if idx is not None and idx < len(temps):
        return float(temps[idx])

    return 20.0


async def _fetch_aqi_once(lat: float, lon: float, at: dt.datetime) -> int:
    at = ensure_aware(at)

    url = (
        "https://air-quality-api.open-meteo.com/v1/air-quality"
        f"?latitude={lat}&longitude={lon}&hourly=us_aqi,pm2_5&timezone=UTC"
    )

    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.get(url)
        r.raise_for_status()
        h = r.json().get("hourly", {})

    times = h.get("time", [])
    aqis = h.get("us_aqi", [])

    idx = _closest_hour_idx(times, at)
    if idx is not None and idx < len(aqis) and aqis[idx] is not None:
        return int(aqis[idx])

    return 60


def _compute_hori(temp_c: float, aqi: int):
    aqi_pen = 0.12 * min(aqi, 500)
    heat = max(0, temp_c - 25) * 1.2
    cold = max(0, 5 - temp_c) * 2.0

    score = max(0, min(100, 100 - (aqi_pen + heat + cold)))

    reasons = {
        "air_quality": aqi_pen,
        "heat": heat,
        "cold": cold,
        "ok": 0,
    }

    reason = max(["air_quality", "heat", "cold"], key=lambda k: reasons[k])
    if reasons[reason] < 1:
        reason = "ok"

    return int(round(score)), reason


# ---- Main HORI Enrichment ----
async def enrich_segments_with_eta(points: List[SegmentPoint], depart_iso: str, duration_min: float):
    depart_utc = parse_iso(depart_iso)
    total_s = duration_min * 60

    # Compute weather once from midpoint
    mid = points[len(points) // 2]

    temp = await _fetch_temp_once(mid.lat, mid.lon, depart_utc)
    aqi = await _fetch_aqi_once(mid.lat, mid.lon, depart_utc)
    hori_score, reason = _compute_hori(temp, aqi)

    enriched = []

    for p in points:
        eta = depart_utc + dt.timedelta(seconds=p.frac * total_s)
        eta = ensure_aware(eta)

        enriched.append(
            HoriSegment(
                lon=p.lon,
                lat=p.lat,
                ts=_iso(eta),
                temp_c=temp,
                aqi=aqi,
                hori=hori_score,
                reason=reason,
            )
        )

    summary = HoriSummary(
        avg_hori=hori_score,
        worst_hori=hori_score,
        worst_idx=0,
        max_aqi=aqi,
        avg_temp_c=temp,
    )

    arrive = ensure_aware(depart_utc + dt.timedelta(seconds=total_s))

    return enriched, summary, arrive
