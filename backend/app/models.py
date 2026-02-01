from typing import List, Optional, Literal
from pydantic import BaseModel, Field
from datetime import datetime

Coord = List[float]

# --------------------------
# REQUEST MODELS
# --------------------------

class RouteRequest(BaseModel):
    src: Coord = Field(..., description="[lon, lat]")
    dst: Coord = Field(..., description="[lon, lat]")
    stops: List[Coord] = []

    # ✅ NEW FIELDS
    src_name: Optional[str] = None
    dst_name: Optional[str] = None
    stop_names: Optional[List[str]] = None

    depart_iso: Optional[str] = None


class SegmentPoint(BaseModel):
    lon: float
    lat: float
    frac: float = 0.0
    ts: Optional[str] = None


# --------------------------
# HORI RESPONSE MODELS
# --------------------------

class HoriSegment(BaseModel):
    lon: float
    lat: float
    ts: str
    temp_c: float
    aqi: int
    hori: int
    reason: Literal["air_quality", "heat", "cold", "ok"]


class HoriSummary(BaseModel):
    avg_hori: float
    worst_hori: int
    worst_idx: int
    max_aqi: int
    avg_temp_c: float


class HoriRouteResponse(BaseModel):
    segments: List[HoriSegment]
    summary: HoriSummary
    distance_km: float
    duration_min: float
    depart_iso: str
    arrive_iso: str


class Echo(BaseModel):
    payload: dict


# --------------------------
# TRIP HISTORY OUTPUT MODELS
# --------------------------

class SegmentOut(BaseModel):
    id: int
    idx: int
    lon: float
    lat: float
    ts: str
    temp_c: float
    aqi: int
    hori: int
    reason: Literal["air_quality", "heat", "cold", "ok"]

    class Config:
        orm_mode = True


class TripSummaryOut(BaseModel):
    id: int
    created_at: datetime

    src_lon: float
    src_lat: float
    dst_lon: float
    dst_lat: float

    # ✅ NEW FIELDS
    src_name: Optional[str] = None
    dst_name: Optional[str] = None
    stop_names: Optional[List[str]] = []

    distance_km: float
    duration_min: float
    depart_iso: str
    arrive_iso: str

    avg_hori: float
    worst_hori: int
    max_aqi: int

    class Config:
        orm_mode = True


class TripDetailOut(TripSummaryOut):
    segments: List[SegmentOut] = []

    class Config:
        orm_mode = True


class SearchedPointOut(BaseModel):
    id: int
    place_name: str
    lat: float
    lon: float
    hori: int
    aqi: int
    temp_c: float
    reason: str
    created_at: datetime

    class Config:
        from_attributes = True
