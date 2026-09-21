from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app.schemas import TrafficSummaryResponse
from backend.app.services.traffic import get_traffic_kpi_summary, get_city_congestion_heatmap, get_origin_destination_matrix

router = APIRouter(prefix="/traffic", tags=["Macro Traffic Analytics"])

@router.get("/summary", response_model=TrafficSummaryResponse)
@router.get("/kpis", response_model=TrafficSummaryResponse)
def traffic_summary(db: Session = Depends(get_db)):
    return get_traffic_kpi_summary(db)

@router.get("/heatmap")
def traffic_heatmap(db: Session = Depends(get_db)):
    return get_city_congestion_heatmap(db)

@router.get("/od", tags=["Origin Destination"])
def origin_destination_matrix():
    return get_origin_destination_matrix()

@router.get("/flow")
def traffic_flow_corridors(db: Session = Depends(get_db)):
    """Returns arterial flow corridors with real-time velocity and volume (Section 45)."""
    heatmap_data = get_city_congestion_heatmap(db)
    return {"corridors": heatmap_data.get("corridors", []), "total_corridors": len(heatmap_data.get("corridors", []))}

@router.get("/congestion")
def traffic_congestion_hotspots(db: Session = Depends(get_db)):
    """Returns active bottleneck junctions with severity index and status (Section 45)."""
    heatmap_data = get_city_congestion_heatmap(db)
    points = heatmap_data.get("heat_points", [])
    congested = [p for p in points if p.get("intensity", 0) >= 0.5]
    return {
        "active_bottlenecks": len(congested),
        "hotspots": congested,
        "severest_bottleneck": min(points, key=lambda x: x.get("speed_kmh", 100)) if points else None
    }

