# app/routers/hori_router.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import datetime as dt
import json

from app.database import SessionLocal
from app import hori
from app.models import RouteRequest, HoriRouteResponse
from app.db_models import SearchedPoint, Trip, Segment as TripSegment


def now_utc():
    return dt.datetime.now(dt.timezone.utc)


router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ---------------------------------------------------------
# Helper: Convert stored JSON text "[]" → python list []
# ---------------------------------------------------------
def parse_stop_names(raw):
    if not raw:
        return []
    try:
        return json.loads(raw)
    except:
        return []


# ----------------------------------------
# SIMPLE HORI POINT
# ----------------------------------------
@router.get("/hori")
async def hori_point(lat: float, lon: float):
    now = now_utc()
    temp = await hori._fetch_temp_once(lat, lon, now)
    aqi = await hori._fetch_aqi_once(lat, lon, now)
    hori_score, reason = hori._compute_hori(temp, aqi)

    return {
        "lat": lat,
        "lon": lon,
        "temp_c": temp,
        "aqi": aqi,
        "hori": hori_score,
        "reason": reason,
    }


# ----------------------------------------
# SAVE HORI POINT
# ----------------------------------------
@router.post("/hori/point")
async def save_hori_point(lat: float, lon: float, place_name: str, db: Session = Depends(get_db)):
    now = now_utc()

    temp = await hori._fetch_temp_once(lat, lon, now)
    aqi = await hori._fetch_aqi_once(lat, lon, now)
    hori_score, reason = hori._compute_hori(temp, aqi)

    row = SearchedPoint(
        place_name=place_name,
        lat=lat,
        lon=lon,
        temp_c=temp,
        aqi=aqi,
        hori=hori_score,
        reason=reason,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


# ----------------------------------------
# LIST SEARCHED POINTS
# ----------------------------------------
@router.get("/searched")
def list_searched(db: Session = Depends(get_db)):
    return db.query(SearchedPoint).order_by(SearchedPoint.id.desc()).all()


@router.get("/searched/{point_id}")
def get_searched(point_id: int, db: Session = Depends(get_db)):
    row = db.query(SearchedPoint).filter(SearchedPoint.id == point_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Not found")
    return row


# ----------------------------------------
# HORI ROUTE (OSRM)
# ----------------------------------------
@router.post("/hori/route", response_model=HoriRouteResponse)
async def hori_route(req: RouteRequest, db: Session = Depends(get_db)):
    from app.osrm import get_osrm_route

    pts, distance_km, duration_min = await get_osrm_route(req.src, req.dst, req.stops)

    depart = (
        dt.datetime.fromisoformat(req.depart_iso.replace("Z", "+00:00"))
        if req.depart_iso else now_utc()
    )

    enriched, summary, arrive = await hori.enrich_segments_with_eta(
        pts, depart, duration_min
    )

    # ----------------------------------------
    # SAVE TRIP WITH NEW FIELDS
    # ----------------------------------------
    trip = Trip(
        src_lon=req.src[0],
        src_lat=req.src[1],
        dst_lon=req.dst[0],
        dst_lat=req.dst[1],
        distance_km=distance_km,
        duration_min=duration_min,
        depart_iso=depart.isoformat().replace("+00:00", "Z"),
        arrive_iso=arrive.isoformat().replace("+00:00", "Z"),
        avg_hori=summary.avg_hori,
        worst_hori=summary.worst_hori,
        worst_idx=summary.worst_idx,
        max_aqi=summary.max_aqi,
        avg_temp_c=summary.avg_temp_c,

        # NEW
        src_name=req.src_name,
        dst_name=req.dst_name,
        stop_names=json.dumps(req.stop_names or []),
    )

    db.add(trip)
    db.commit()
    db.refresh(trip)

    # Save segments as usual
    for i, s in enumerate(enriched):
        db.add(
            TripSegment(
                trip_id=trip.id,
                idx=i,
                lon=s.lon,
                lat=s.lat,
                ts=s.ts,
                temp_c=s.temp_c,
                aqi=s.aqi,
                hori=s.hori,
                reason=s.reason,
            )
        )
    db.commit()

    # ------------------------------
    # RETURN RESPONSE
    # ------------------------------
    # No change needed here
    return HoriRouteResponse(
        segments=enriched,
        summary=summary,
        distance_km=distance_km,
        duration_min=duration_min,
        depart_iso=trip.depart_iso,
        arrive_iso=trip.arrive_iso,
    )
