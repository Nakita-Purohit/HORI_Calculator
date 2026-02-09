# app/routers/search_router.py

from fastapi import APIRouter, HTTPException
import httpx

router = APIRouter()

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"


@router.get("/search")
async def search_address(q: str):
    if not q or len(q) < 3:
        return []

    params = {
        "q": q,
        "format": "json",
        "addressdetails": 1,
        "limit": 5
    }

    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.get(NOMINATIM_URL, params=params)

    if r.status_code != 200:
        raise HTTPException(500, "Geocoding failed")

    results = r.json()

    formatted = []
    for item in results:
        formatted.append({
            "display_name": item.get("display_name"),
            "lat": float(item.get("lat")),
            "lon": float(item.get("lon")),
            "place_name": item.get("display_name"),
        })

    return formatted
