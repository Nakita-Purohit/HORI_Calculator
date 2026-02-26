// App.jsx
import React, { useState } from "react";
import MapComponent from "./components/MapComponent";
import SearchBar from "./components/SearchBar";
import DirectionsPanel from "./components/DirectionsPanel";
import TripReviewPanel from "./components/TripReviewPanel";
import "./App.css";

export default function App() {
  const [selected, setSelected] = useState(null);
  const [mode, setMode] = useState("search");
  const [destination, setDestination] = useState(null);
  const [routeResult, setRouteResult] = useState(null);
  const [showTripReview, setShowTripReview] = useState(false);

  function handleSelect(item) {
    setSelected(item);
    setMode("search");
  }

  function handleGetDirections(dest) {
    setDestination(dest);
    setMode("directions");
  }

  function handleRouteReady(routeData) {
    setRouteResult(routeData);
    setSelected(null);
    setShowTripReview(true);   // ⭐ Show Trip Review Panel
    setMode("search");
  }

  async function handleUpdateRoute(updated) {
    const body = {
      src: [updated.src.lon, updated.src.lat],
      dst: [updated.dst.lon, updated.dst.lat],
      stops: updated.stops.filter(Boolean).map(s => [s.lon, s.lat]),
      depart_iso: new Date().toISOString(),
    };

    const res = await fetch("/api/hori/route", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });

    const data = await res.json();

    setRouteResult({
      src: updated.src,
      dst: updated.dst,
      stops: updated.stops,
      segments: data.segments,
      distance_km: data.distance_km,
      duration_min: data.duration_min
    });
  }

  return (
    <div>
      <MapComponent
        selected={selected}
        routeResult={routeResult}
        onGetDirections={handleGetDirections}
      />

      {!showTripReview && mode === "search" && (
        <SearchBar onSelect={handleSelect} />
      )}

      {!showTripReview && mode === "directions" && (
        <DirectionsPanel
          destination={destination}
          onDone={handleRouteReady}
          onBack={() => setMode("search")}
        />
      )}

      {showTripReview && routeResult && (
        <TripReviewPanel
          route={routeResult}
          onUpdateRoute={handleUpdateRoute}
          onBack={() => setShowTripReview(false)}
        />
      )}
    </div>
  );
}
