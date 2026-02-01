# app/osrm.py
import httpx
import polyline
from .models import SegmentPoint

# IMPORTANT FIX — use localhost instead of host.docker.internal
OSRM_BASE_URL = "http://osrm:5000"


async def get_osrm_route(src, dst, stops):
    all_points = [src] + stops + [dst]
    coords_str = ";".join([f"{lon},{lat}" for lon, lat in all_points])

    url = (
        f"{OSRM_BASE_URL}/route/v1/driving/{coords_str}"
        "?overview=full&geometries=polyline6&steps=false"
    )

    async with httpx.AsyncClient(timeout=10.0) as client:
        r = await client.get(url)
        r.raise_for_status()
        data = r.json()

    if "routes" not in data or not data["routes"]:
        raise Exception("Invalid OSRM response.")

    route = data["routes"][0]

    geom = route.get("geometry")
    if not geom:
        raise Exception("No geometry returned from OSRM")

    decoded = polyline.decode(geom, precision=6)

    total = len(decoded)
    STEP = max(1, total // 200)
    sampled = decoded[::STEP]
    if sampled[-1] != decoded[-1]:
        sampled.append(decoded[-1])

    points = [
        SegmentPoint(lon=lon, lat=lat, frac=i / max(1, len(sampled) - 1))
        for i, (lat, lon) in enumerate(sampled)
    ]

    distance_km = route["distance"] / 1000.0
    duration_min = route["duration"] / 60.0

    return points, distance_km, duration_min
