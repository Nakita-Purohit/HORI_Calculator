import React, { useState } from "react";
import { searchAddress } from "../lib/api";

export default function AutoInput({ value, placeholder, onSelect }) {
  const [query, setQuery] = useState(value || "");
  const [list, setList] = useState([]);

  async function change(e) {
    const q = e.target.value;
    setQuery(q);

    if (q.length < 3) return setList([]);

    const results = await searchAddress(q);
    setList(results || []);
  }

  function choose(item) {
    const lat = parseFloat(item.lat);
    const lon = parseFloat(item.lon);

    onSelect({
      place_name: item.display_name,
      lat,
      lon,
    });
    setList([]);
    setQuery(item.display_name);
  }

  return (
    <div style={{ position: "relative", width: "100%" }}>
      <input
        value={query}
        placeholder={placeholder}
        onChange={change}
      />

      {list.length > 0 && (
        <div className="suggestions">
          {list.map((item, idx) => (
            <div key={idx} className="suggestion-item" onClick={() => choose(item)}>
              {item.display_name}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
