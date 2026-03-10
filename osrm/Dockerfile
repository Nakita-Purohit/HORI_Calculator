FROM osrm/osrm-backend:latest

# Copy your route files
COPY data/ /data

# Run OSRM in MLD mode (fast routing)
CMD ["osrm-routed", "--algorithm", "MLD", "/data/pa-latest.osrm"]
