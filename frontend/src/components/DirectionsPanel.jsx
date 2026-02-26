// DirectionsPanel.jsx
import React, { useState, useEffect } from "react";
import AutoInput from "./AutoInput";
import "./DirectionsPanel.css";

export default function DirectionsPanel({ destination, onBack, onDone }) {
  const [src, setSrc] = useState(null);
  const [dst, setDst] = useState(destination || null);
  const [stops, setStops] = useState([]);

  useEffect(() => {
    if (destination) setDst(destination);
  }, [destination]);

  function addStop() {
    setStops([...stops, null]);
  }

  async function fetchRoute() {
    if (!src || !dst) {
      alert("Please choose both source and destination.");
      return;
    }

    const body = {
      src: [src.lon, src.lat],
      dst: [dst.lon, dst.lat],
      stops: stops.filter(Boolean).map(s => [s.lon, s.lat]),
      depart_iso: new Date().toISOString(),
    };

    const res = await fetch("/api/hori/route", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });

    const data = await res.json();

    onDone({
      src,
      dst,
      stops,
      segments: data.segments,
      distance_km: data.distance_km,
      duration_min: data.duration_min
    });
  }

  return (
    <div className="directions-panel">
      <button className="back-btn" onClick={onBack}>← Back to Search</button>

      <div className="input-wrapper">
        <AutoInput
          placeholder="Choose starting point..."
          value={src?.place_name || ""}
          onSelect={setSrc}
        />
      </div>

      <div className="input-wrapper">
        <AutoInput
          placeholder="Destination..."
          value={dst?.place_name || ""}
          onSelect={setDst}
        />
      </div>

      {stops.map((s, i) => (
        <div key={i} className="input-wrapper">
          <AutoInput
            placeholder={`Stop ${i + 1}`}
            value={s?.place_name || ""}
            onSelect={val => {
              const updated = [...stops];
              updated[i] = val;
              setStops(updated);
            }}
          />
        </div>
      ))}

      <button className="add-stop-btn" onClick={addStop}>+ Add Stop</button>

      <button className="route-btn" onClick={fetchRoute}>Get Trip Route</button>
    </div>
  );
}
