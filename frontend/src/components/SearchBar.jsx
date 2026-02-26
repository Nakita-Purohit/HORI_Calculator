import React, { useState } from "react";
import { searchAddress, getHori } from "../lib/api";
import "./SearchBar.css";

export default function SearchBar({ onSelect }) {
  const [query, setQuery] = useState("");
  const [list, setList] = useState([]);

  async function handleChange(e) {
    const q = e.target.value;
    setQuery(q);

    if (q.length < 3) return setList([]);

    const res = await searchAddress(q);
    setList(res || []);
  }

  async function choose(item) {
    const lat = parseFloat(item.lat);
    const lon = parseFloat(item.lon);

    const hori = await getHori(lat, lon, item.display_name);

    onSelect({
      place_name: item.display_name,
      lat,
      lon,
      ...hori,
    });

    setList([]);
  }

  return (
    <div className="search-container">
      <input
        value={query}
        placeholder="Search location"
        onChange={handleChange}
        className="search-box"
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
