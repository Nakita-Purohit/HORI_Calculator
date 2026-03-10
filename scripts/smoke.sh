#!/usr/bin/env bash
set -euo pipefail
HOST=${1:-http://localhost:8000}


printf "\n[1/3] healthz...\n"
curl -s "$HOST/healthz" | jq .


printf "\n[2/3] /route (mock or ORS)...\n"
curl -s -X POST "$HOST/route" \
-H 'Content-Type: application/json' \
-d '{"src":[-75.6,39.96],"dst":[-75.16,39.95]}' | jq '.points | length'


printf "\n[3/3] /hori/route (compute)...\n"
curl -s -X POST "$HOST/hori/route" \
-H 'Content-Type: application/json' \
-d '{"src":[-75.6,39.96],"dst":[-75.16,39.95]}' | jq '{avg: .summary.avg_hori, worst: .summary.worst_hori, n: (.segments|length)}'
