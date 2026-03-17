# HORI – Health-Oriented Risk Index

HORI is a health-aware route planning web application that helps users choose routes not only based on distance or travel time but also environmental health risk.

The system analyzes **temperature and air quality (AQI)** along routes and computes a **Health-Oriented Risk Index (HORI)** to highlight safer travel paths.

---

## Overview

Traditional navigation tools optimize only for **distance or travel time**.  
HORI extends this idea by adding **environmental risk awareness**.

Users can:

- Search for locations on an interactive map
- View **temperature, AQI, and HORI risk score**
- Generate routes between locations
- See **health risk levels at route stops**
- Visualize routes and risk markers on the map

The system is implemented as a **Kubernetes-native full-stack application deployed on CloudLab**.

---

## Tech Stack

### Frontend
- React
- React-Leaflet
- Leaflet

### Backend
- FastAPI (Python REST API)

### Routing
- Open Source Routing Machine (OSRM)

### Database
- PostgreSQL

### Infrastructure
- Docker
- Kubernetes (CloudLab)

---

## System Architecture

HORI follows a **microservice-based architecture deployed on Kubernetes**.

Main components:

- Frontend (React + Leaflet)
- Backend API (FastAPI)
- Routing Engine (OSRM)
- Database (PostgreSQL)

Workflow:

1. User searches for a location or route
2. Frontend sends request to backend
3. Backend calls OSRM to compute route geometry
4. Backend retrieves temperature and AQI data from external APIs
5. HORI score is calculated
6. Results are stored in PostgreSQL
7. Frontend displays route and risk information on the map

---

## Kubernetes Deployment

The application runs as multiple Kubernetes deployments:

- **Frontend Deployment**
  - React UI served through nginx
  - Exposed externally via NodePort

- **Backend Deployment**
  - FastAPI service providing REST endpoints
  - Communicates with OSRM and PostgreSQL

- **OSRM Deployment**
  - Provides route geometry and distance calculations

- **PostgreSQL Deployment**
  - Stores trip history and route metadata
  - Uses PersistentVolumeClaim for persistent storage

Internal communication occurs through **ClusterIP services**, ensuring only the frontend is externally exposed.

---

## Persistence

PostgreSQL stores:

- Trip metadata
- Route geometry
- Segment-level environmental data
- HORI risk scores

PersistentVolumeClaims ensure that **database data survives pod restarts and redeployments**.

---

## Known Limitations

- Routing currently focused on Pennsylvania data
- No Horizontal Pod Autoscaler configured
- Basic observability using kubectl logs
- No authentication or user accounts
- HORI model currently uses only temperature and AQI

---

## Future Improvements

- Horizontal Pod Autoscaling
- Additional environmental factors (UV index, pollen)
- Authentication and user profiles
- Observability with Prometheus and Grafana
- CI/CD pipeline using GitHub Actions

---

## Contributors

- Sai Guddeti – Project Lead  
- Nakita Ramachandra Purohit – Backend & Risk Processing  
- Param Upadhyay – DevOps  
- Priyanka Tentu – QA & Documentation
