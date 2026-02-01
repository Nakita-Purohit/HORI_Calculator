# app/main.py
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timezone
import httpx
import json

from app.routers import hori_router
from app.models import TripSummaryOut, TripDetailOut

from .database import SessionLocal, engine
from .db_models import Base, Trip, Segment, SearchedPoint
from .models import (
    RouteRequest,
    HoriRouteResponse,
    SearchedPointOut,
)

from .hori import (
    enrich_segments_with_eta,
    _fetch_temp_once,
    _fetch_aqi_once,
    _compute_hori,
)


# ============================================================
# FASTAPI + DB INIT
# ============================================================

app = FastAPI(title="HORI Backend API", openapi_prefix="/api")
Base.metadata.create_all(bind=engine)

# ✅ FIXED CORS — correct syntax
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(hori_router.router)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ============================================================
# UTIL HELPERS
# ============================================================

def parse_stop_names(raw):
    """Convert DB text → Python list."""
    if not raw:
        return []
    try:
        return json.loads(raw)
    except:
        return []


# ============================================================
# SEARCH ENDPOINT (WORKING)
# ============================================================

@app.get("/search")
async def search_address(q: str = Query(..., min_length=2)):

    url = "https://nominatim.openstreetmap.org/search"
    params = {"format": "json", "addressdetails": 1, "q": q, "limit": 8}
    headers = {"User-Agent": "HORI-App/1.0 (contact@example.com)"}

    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.get(url, params=params, headers=headers)

    if r.status_code != 200:
        raise HTTPException(500, f"Nominatim Error {r.status_code}")

    results = []
    for item in r.json():
        results.append({
            "place_name": item.get("display_name"),
            "lat": float(item.get("lat")),
            "lon": float(item.get("lon")),
        })

    return results


# ============================================================
# ROOT
# ============================================================

@app.get("/")
def root():
    return {"status": "ok", "msg": "HORI backend running"}


# ============================================================
# HORI POINT
# ============================================================

@app.get("/hori")
async def hori_point(lat: float, lon: float):
    return await _compute_point_hori(lat, lon)


async def _compute_point_hori(lat: float, lon: float):
    now = datetime.now(timezone.utc)
    temp_c = await _fetch_temp_once(lat, lon, now)
    aqi = await _fetch_aqi_once(lat, lon, now)
    hori_val, reason = _compute_hori(temp_c, aqi)

    return {
        "lat": lat,
        "lon": lon,
        "temp_c": temp_c,
        "aqi": aqi,
        "hori": hori_val,
        "reason": reason,
    }


# ============================================================
# SAVE HORI POINT
# ============================================================

@app.post("/hori/point", response_model=SearchedPointOut)
async def save_point_hori(
    lat: float,
    lon: float,
    place_name: str = Query("Unknown location"),
    db: Session = Depends(get_db),
):

    data = await _compute_point_hori(lat, lon)

    entry = SearchedPoint(
        place_name=place_name,
        lat=lat,
        lon=lon,
        temp_c=data["temp_c"],
        aqi=data["aqi"],
        hori=data["hori"],
        reason=data["reason"],
        created_at=datetime.utcnow(),
    )

    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


# ============================================================
# SEARCHED HISTORY
# ============================================================

@app.get("/searched", response_model=List[SearchedPointOut])
def list_searched(limit: int = 50, db: Session = Depends(get_db)):
    return (
        db.query(SearchedPoint)
        .order_by(SearchedPoint.created_at.desc())
        .limit(limit)
        .all()
    )


@app.get("/searched/{point_id}", response_model=SearchedPointOut)
def get_searched(point_id: int, db: Session = Depends(get_db)):
    p = db.query(SearchedPoint).filter(SearchedPoint.id == point_id).first()
    if not p:
        raise HTTPException(404, "Not found")
    return p


# ============================================================
# HORI ROUTE
# ============================================================

@app.post("/hori/route", response_model=HoriRouteResponse)
async def hori_route(req: RouteRequest, db: Session = Depends(get_db)):

    from .osrm import get_osrm_route

    seg_points, distance_km, duration_min = await get_osrm_route(
        req.src, req.dst, req.stops
    )

    depart_utc = datetime.now(timezone.utc)

    segments, summary, arrive_utc = await enrich_segments_with_eta(
        seg_points, depart_utc, duration_min
    )

    depart_iso = depart_utc.isoformat()
    arrive_iso = arrive_utc.isoformat()

    trip = Trip(
        src_lon=req.src[0],
        src_lat=req.src[1],
        dst_lon=req.dst[0],
        dst_lat=req.dst[1],
        distance_km=distance_km,
        duration_min=duration_min,
        avg_hori=summary.avg_hori,
        worst_hori=summary.worst_hori,
        worst_idx=summary.worst_idx,
        max_aqi=summary.max_aqi,
        avg_temp_c=summary.avg_temp_c,
        depart_iso=depart_iso,
        arrive_iso=arrive_iso,
        created_at=datetime.utcnow(),

        # NEW
        src_name=req.src_name,
        dst_name=req.dst_name,
        stop_names=json.dumps(req.stop_names or []),
    )

    db.add(trip)
    db.commit()
    db.refresh(trip)

    for idx, seg in enumerate(segments):
        db.add(
            Segment(
                trip_id=trip.id,
                idx=idx,
                lon=seg.lon,
                lat=seg.lat,
                ts=seg.ts,
                temp_c=seg.temp_c,
                aqi=seg.aqi,
                hori=seg.hori,
                reason=seg.reason,
            )
        )

    db.commit()

    return HoriRouteResponse(
        segments=segments,
        summary=summary,
        distance_km=distance_km,
        duration_min=duration_min,
        depart_iso=depart_iso,
        arrive_iso=arrive_iso,
    )


# ============================================================
# TRIPS LIST (FIXED)
# ============================================================

@app.get("/trips", response_model=List[TripSummaryOut])
def list_trips(limit: int = 20, db: Session = Depends(get_db)):

    trips = (
        db.query(Trip)
        .order_by(Trip.created_at.desc())
        .limit(limit)
        .all()
    )

    # FIX: convert DB text to list
    for t in trips:
        t.stop_names = parse_stop_names(t.stop_names)

    return trips


# ============================================================
# TRIP DETAILS (FIXED)
# ============================================================

@app.get("/trips/{trip_id}", response_model=TripDetailOut)
def get_trip(trip_id: int, db: Session = Depends(get_db)):

    trip = db.query(Trip).filter(Trip.id == trip_id).first()
    if not trip:
        raise HTTPException(404, "Trip not found")

    # FIX JSON field
    trip.stop_names = parse_stop_names(trip.stop_names)

    trip.segments  # lazy load

    return trip
