# app/db_models.py
from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from .database import Base


def utc_now():
    """Generate a timezone-aware UTC timestamp."""
    return datetime.now(timezone.utc)


class SearchedPoint(Base):
    __tablename__ = "searched_points"

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    place_name = Column(String, nullable=True)
    lat = Column(Float, nullable=False)
    lon = Column(Float, nullable=False)

    hori = Column(Integer, nullable=False)
    aqi = Column(Integer, nullable=False)
    temp_c = Column(Float, nullable=False)
    reason = Column(String, nullable=False)


class Trip(Base):
    __tablename__ = "trips"

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    src_lon = Column(Float, nullable=False)
    src_lat = Column(Float, nullable=False)
    dst_lon = Column(Float, nullable=False)
    dst_lat = Column(Float, nullable=False)

    distance_km = Column(Float, nullable=False)
    duration_min = Column(Float, nullable=False)

    depart_iso = Column(String, nullable=False)
    arrive_iso = Column(String, nullable=False)

    avg_hori = Column(Float, nullable=False)
    worst_hori = Column(Integer, nullable=False)
    worst_idx = Column(Integer, nullable=False)
    max_aqi = Column(Integer, nullable=False)
    avg_temp_c = Column(Float, nullable=False)

    # ✅ NEW FIELDS
    src_name = Column(String, nullable=True)
    dst_name = Column(String, nullable=True)
    stop_names = Column(Text, default="[]")  # JSON list as text

    segments = relationship("Segment", back_populates="trip", cascade="all, delete-orphan")


class Segment(Base):
    __tablename__ = "segments"

    id = Column(Integer, primary_key=True, index=True)
    trip_id = Column(Integer, ForeignKey("trips.id"))
    idx = Column(Integer, nullable=False)

    lon = Column(Float, nullable=False)
    lat = Column(Float, nullable=False)

    ts = Column(String, nullable=False)

    temp_c = Column(Float, nullable=False)
    aqi = Column(Integer, nullable=False)
    hori = Column(Integer, nullable=False)
    reason = Column(String, nullable=False)

    trip = relationship("Trip", back_populates="segments")
