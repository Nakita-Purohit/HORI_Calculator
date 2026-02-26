// icons.jsx
import React from "react";

export function SwapIcon({ size = 20 }) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <polyline points="17 1 21 5 17 9" />
      <line x1="21" y1="5" x2="3" y2="5" />

      <polyline points="7 23 3 19 7 15" />
      <line x1="3" y1="19" x2="21" y2="19" />
    </svg>
  );
}
