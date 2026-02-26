// MapComponent.jsx
import React, { useEffect, useState } from "react";
import { MapContainer, TileLayer, Marker, Popup, Polyline, useMap } from "react-leaflet";
import L from "leaflet";
import "leaflet/dist/leaflet.css";

// 🟢 Green (Safe)
const greenIcon = new L.Icon({
  iconUrl:
    "https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-green.png",
  shadowUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
});

// 🟡 Yellow (Low Risk)
const yellowIcon = new L.Icon({
  iconUrl:
    "https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-gold.png",
  shadowUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
});

// 🟠 Orange (Moderate)
const orangeIcon = new L.Icon({
  iconUrl:
    "https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-orange.png",
  shadowUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
});

// 🔴 Red (High Risk)
const redIcon = new L.Icon({
  iconUrl:
    "https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-red.png",
  shadowUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
});

// HORI color rule
function getHoriIcon(hori) {
  if (hori >= 85) return greenIcon;
  if (hori >= 70) return yellowIcon;
  if (hori >= 50) return orangeIcon;
  return redIcon;
}

// 🔍 Find segment closest to a marker → to display HORI popup
function findClosestSegment(lat, lon, segments) {
  if (!segments || !segments.length) return null;

  let best = null;
  let minDist = Infinity;

  for (const s of segments) {
    const dx = s.lat - lat;
    const dy = s.lon - lon;
    const d = dx * dx + dy * dy;
    if (d < minDist) {
      minDist = d;
      best = s;
    }
  }
  return best;
}

function FlyToLocation({ selected }) {
  const map = useMap();

  useEffect(() => {
    if (selected) {
      map.flyTo([selected.lat, selected.lon], 15, { duration: 1.2 });
    }
  }, [selected]);

  return null;
}

function FitRoute({ coords }) {
  const map = useMap();
  useEffect(() => {
    if (coords && coords.length > 1) {
      const bounds = L.latLngBounds(coords);
      map.fitBounds(bounds, { padding: [50, 50] });
    }
  }, [coords]);
  return null;
}

export default function MapComponent({ selected, routeResult, onGetDirections }) {

  const [polyline, setPolyline] = useState(null);

  // ⭐ Convert backend segments → polyline coordinates
  useEffect(() => {
    if (routeResult?.segments?.length) {
      const coords = routeResult.segments.map(s => [s.lat, s.lon]);
      setPolyline(coords);
    } else {
      setPolyline(null);
    }
  }, [routeResult]);

  /* Source / Stops / Destination markers */
  const srcMarker = routeResult?.src;
  const dstMarker = routeResult?.dst;
  const stopMarkers = routeResult?.stops || [];

  const iconToUse = selected ? getHoriIcon(selected.hori) : greenIcon;

  return (
    <MapContainer
      center={[39.96, -75.6]}
      zoom={12}
      style={{ height: "100vh", width: "100%" }}
      zoomControl={false}
    >
      <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />

      {/* Fly to searched location */}
      {!polyline && <FlyToLocation selected={selected} />}
      
      {/* Fit to route automatically */}
      {polyline && <FitRoute coords={polyline} />}

      {/* Draw the trip route */}
      {polyline && <Polyline positions={polyline} weight={6} color="blue" />}

      {/* Source marker */}
      {srcMarker && (
        <Marker position={[srcMarker.lat, srcMarker.lon]} icon={greenIcon}>
          <Popup>
            {(() => {
              const info = findClosestSegment(srcMarker.lat, srcMarker.lon, routeResult?.segments);
              return (
                <>
                  <b>Source</b><br />
                  {srcMarker.place_name}<br /><br />

                  {info && (
                    <>
                      HORI: {info.hori}<br />
                      Temp: {info.temp_c} °C<br />
                      AQI: {info.aqi}<br />
                      Reason: {info.reason}<br />
                      Time: {info.ts}<br />
                    </>
                  )}
                </>
              );
            })()}
          </Popup>
        </Marker>
      )}

      {/* Stop markers */}
      {stopMarkers.map((s, i) => (
        <Marker key={i} position={[s.lat, s.lon]} icon={orangeIcon}>
          <Popup>
            {(() => {
              const info = findClosestSegment(s.lat, s.lon, routeResult?.segments);
              return (
                <>
                  <b>Stop {i + 1}</b><br />
                  {s.place_name}<br /><br />

                  {info && (
                    <>
                      HORI: {info.hori}<br />
                      Temp: {info.temp_c} °C<br />
                      AQI: {info.aqi}<br />
                      Reason: {info.reason}<br />
                      Time: {info.ts}<br />
                    </>
                  )}
                </>
              );
            })()}
          </Popup>
        </Marker>
      ))}

      {/* Destination marker */}
      {dstMarker && (
        <Marker position={[dstMarker.lat, dstMarker.lon]} icon={redIcon}>
          <Popup>
            {(() => {
              const info = findClosestSegment(dstMarker.lat, dstMarker.lon, routeResult?.segments);
              return (
                <>
                  <b>Destination</b><br />
                  {dstMarker.place_name}<br /><br />

                  {info && (
                    <>
                      HORI: {info.hori}<br />
                      Temp: {info.temp_c} °C<br />
                      AQI: {info.aqi}<br />
                      Reason: {info.reason}<br />
                      Time: {info.ts}<br /><br />
                    </>
                  )}
                </>
              );
            })()}
          </Popup>
        </Marker>
      )}

      {/* Only show popup when no route is shown */}
      {!polyline && selected && (
        <Marker position={[selected.lat, selected.lon]} icon={iconToUse}>
          <Popup>
            <b>{selected.place_name}</b> <br />
            HORI: {selected.hori} <br />
            Temp: {selected.temp_c} °C <br />
            AQI: {selected.aqi} <br />
            Reason: {selected.reason}
            <br /><br />
            <button
              className="popup-directions-btn"
              onClick={() => onGetDirections(selected)}
            >
              Get Directions
            </button>
          </Popup>
        </Marker>
      )}
    </MapContainer>
  );
}
