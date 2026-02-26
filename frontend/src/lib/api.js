const NOMINATIM = "https://nominatim.openstreetmap.org/search";

export async function searchAddress(query) {
  try {
    const url = `${NOMINATIM}?format=json&q=${encodeURIComponent(query)}&addressdetails=1&limit=5`;
    const res = await fetch(url, {
      headers: { "Accept": "application/json" }
    });
    return await res.json();
  } catch (e) {
    console.error("Search error:", e);
    return [];
  }
}

// Fetch HORI from backend when a user selects an address
export async function getHori(lat, lon, place) {
  const url = `/api/hori/point?lat=${lat}&lon=${lon}&place_name=${encodeURIComponent(place)}`;
  const res = await fetch(url, { method: "POST" });
  return res.json();
}
