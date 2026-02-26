// TripReviewPanel.jsx
import React, { useState } from "react";
import AutoInput from "./AutoInput";
import "./DirectionsPanel.css";

export default function TripReviewPanel({ route, onUpdateRoute, onBack }) {
  const [src, setSrc] = useState(route.src);
  const [dst, setDst] = useState(route.dst);
  const [stops, setStops] = useState(route.stops || []);

  function updateRoute() {
    onUpdateRoute({
      src,
      dst,
      stops
    });
  }

  function removeStop(i) {
    const arr = [...stops];
    arr.splice(i, 1);
    setStops(arr);
  }

  // ⭐ Convert KM → Miles
  const miles = route.distance_km
    ? (route.distance_km * 0.621371).toFixed(2)
    : null;

  // ⭐ Convert minutes → hours + mins
  let durationText = "";
  if (route.duration_min != null) {
    const hours = Math.floor(route.duration_min / 60);
    const mins = Math.round(route.duration_min % 60);
    durationText = `${hours} hr ${mins} min`;
  }

  return (
    <div className="directions-panel">

      <h3>Trip Summary</h3>

      <div className="trip-info">
        <p>
          <b>Distance:</b> {miles ? `${miles} miles` : "—"}
        </p>
        <p>
          <b>Duration:</b> {durationText || "—"}
        </p>
      </div>

      <AutoInput
        placeholder="Source"
        value={src?.place_name || ""}
        onSelect={setSrc}
      />

      {stops.map((s, i) => (
        <div key={i} className="input-wrapper">
          <AutoInput
            placeholder={`Stop ${i + 1}`}
            value={s?.place_name || ""}
            onSelect={(val) => {
              const arr = [...stops];
              arr[i] = val;
              setStops(arr);
            }}
          />
          <button
            className="remove-stop-btn"
            onClick={() => removeStop(i)}
          >
            ✖
          </button>
        </div>
      ))}

      <button
        className="add-stop-btn"
        onClick={() => setStops([...stops, null])}
      >
        + Add Stop
      </button>

      <AutoInput
        placeholder="Destination"
        value={dst?.place_name || ""}
        onSelect={setDst}
      />

      <button className="route-btn" onClick={updateRoute}>
        Update Route
      </button>

      <button className="back-btn" onClick={onBack}>
        ⟵ Back
      </button>
    </div>
  );
}
