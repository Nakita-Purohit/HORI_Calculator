FROM osrm/osrm-backend:latest

# Copies route files
COPY data/ /data

# Runs OSRM in MLD mode (fast routing)
CMD ["osrm-routed", "--algorithm", "MLD", "/data/pa-latest.osrm"]
