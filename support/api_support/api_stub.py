"""
RailOptima API Stub - Mock API endpoints for railway management system
This module provides FastAPI endpoints for testing and development purposes.
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import random
import asyncio
import logging
import os
import sys

# Add the support directory to the path to import data loader
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
try:
    from Sample_Data_Preparation.data_loader import load_sample_data, get_available_scenarios, reload_data
except ImportError:
    # Fallback for different path structures
    sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'Sample Data Preparation'))
    from data_loader import load_sample_data, get_available_scenarios, reload_data

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="RailOptima API",
    description="Railway traffic management and optimization API",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class Train(BaseModel):
    id: str
    name: str
    route: str
    departure_time: datetime
    arrival_time: datetime
    status: str = "scheduled"
    priority: int = Field(ge=1, le=5, description="Priority level 1-5")
    capacity: int = Field(gt=0, description="Passenger capacity")
    current_station: Optional[str] = None
    delay_minutes: int = 0

class Station(BaseModel):
    id: str
    name: str
    location: Dict[str, float]  # {"lat": 0.0, "lng": 0.0}
    capacity: int
    current_trains: int = 0
    status: str = "operational"

class Infrastructure(BaseModel):
    id: str
    type: str  # "track", "signal", "bridge", "tunnel"
    status: str = "operational"
    location: Dict[str, float]
    maintenance_due: Optional[datetime] = None
    capacity: Optional[int] = None

class Disruption(BaseModel):
    id: str
    type: str  # "delay", "cancellation", "track_closure", "signal_failure"
    severity: str  # "low", "medium", "high", "critical"
    affected_trains: List[str]
    affected_stations: List[str]
    start_time: datetime
    estimated_end_time: Optional[datetime] = None
    description: str

class OptimizationRequest(BaseModel):
    trains: List[Train]
    constraints: Dict[str, Any]
    objective: str = "minimize_delays"  # "minimize_delays", "maximize_throughput", "minimize_conflicts"

class OptimizationResponse(BaseModel):
    optimized_trains: List[Train]
    conflicts_resolved: int
    total_delay_reduction: int
    optimization_time: float
    status: str

# Mock data storage
trains_db: List[Train] = []
stations_db: List[Station] = []
infrastructure_db: List[Infrastructure] = []
disruptions_db: List[Disruption] = []
current_scenario: Optional[str] = None

# Initialize with sample data
def initialize_sample_data(scenario: Optional[str] = None):
    """Initialize the API with sample railway data from files"""
    global trains_db, stations_db, infrastructure_db, disruptions_db, current_scenario
    
    try:
        # Load data from files
        sample_data = load_sample_data(scenario)
        current_scenario = scenario
        
        # Convert to Pydantic models
        trains_db = [Train(**train_data) for train_data in sample_data.get("trains", [])]
        stations_db = [Station(**station_data) for station_data in sample_data.get("stations", [])]
        infrastructure_db = [Infrastructure(**infra_data) for infra_data in sample_data.get("infrastructure", [])]
        disruptions_db = [Disruption(**disruption_data) for disruption_data in sample_data.get("disruptions", [])]
        
        logger.info(f"Initialized API with {len(trains_db)} trains, {len(stations_db)} stations, "
                   f"{len(infrastructure_db)} infrastructure components, {len(disruptions_db)} disruptions")
        if scenario:
            logger.info(f"Using scenario: {scenario}")
            
    except Exception as e:
        logger.error(f"Error loading sample data: {e}")
        # Fallback to minimal data
        trains_db = []
        stations_db = []
        infrastructure_db = []
        disruptions_db = []
        logger.warning("Using empty datasets due to loading error")

def reload_sample_data(scenario: Optional[str] = None):
    """Reload sample data from files"""
    logger.info(f"Reloading sample data{' for scenario: ' + scenario if scenario else ''}")
    initialize_sample_data(scenario)

# API Endpoints

@app.on_event("startup")
async def startup_event():
    """Initialize sample data on startup"""
    initialize_sample_data()
    logger.info("RailOptima API initialized with sample data")

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "RailOptima API - Railway Traffic Management System",
        "version": "1.0.0",
        "status": "operational",
        "current_scenario": current_scenario or "default",
        "available_scenarios": get_available_scenarios(),
        "endpoints": {
            "trains": "/trains",
            "stations": "/stations", 
            "infrastructure": "/infrastructure",
            "disruptions": "/disruptions",
            "optimize": "/optimize",
            "health": "/health",
            "metrics": "/metrics",
            "scenarios": "/scenarios",
            "reload": "/reload"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "uptime": "operational",
        "services": {
            "database": "connected",
            "optimization_engine": "ready",
            "monitoring": "active"
        }
    }

# Train endpoints
@app.get("/trains", response_model=List[Train])
async def get_trains():
    """Get all trains"""
    return trains_db

@app.get("/trains/{train_id}", response_model=Train)
async def get_train(train_id: str):
    """Get specific train by ID"""
    train = next((t for t in trains_db if t.id == train_id), None)
    if not train:
        raise HTTPException(status_code=404, detail="Train not found")
    return train

@app.post("/trains", response_model=Train)
async def create_train(train: Train):
    """Create a new train"""
    trains_db.append(train)
    logger.info(f"Created train {train.id}: {train.name}")
    return train

@app.put("/trains/{train_id}", response_model=Train)
async def update_train(train_id: str, train_update: Train):
    """Update train information"""
    train_index = next((i for i, t in enumerate(trains_db) if t.id == train_id), None)
    if train_index is None:
        raise HTTPException(status_code=404, detail="Train not found")
    
    trains_db[train_index] = train_update
    logger.info(f"Updated train {train_id}")
    return train_update

@app.delete("/trains/{train_id}")
async def delete_train(train_id: str):
    """Delete a train"""
    train_index = next((i for i, t in enumerate(trains_db) if t.id == train_id), None)
    if train_index is None:
        raise HTTPException(status_code=404, detail="Train not found")
    
    deleted_train = trains_db.pop(train_index)
    logger.info(f"Deleted train {train_id}: {deleted_train.name}")
    return {"message": f"Train {train_id} deleted successfully"}

# Station endpoints
@app.get("/stations", response_model=List[Station])
async def get_stations():
    """Get all stations"""
    return stations_db

@app.get("/stations/{station_id}", response_model=Station)
async def get_station(station_id: str):
    """Get specific station by ID"""
    station = next((s for s in stations_db if s.id == station_id), None)
    if not station:
        raise HTTPException(status_code=404, detail="Station not found")
    return station

@app.post("/stations", response_model=Station)
async def create_station(station: Station):
    """Create a new station"""
    stations_db.append(station)
    logger.info(f"Created station {station.id}: {station.name}")
    return station

# Infrastructure endpoints
@app.get("/infrastructure", response_model=List[Infrastructure])
async def get_infrastructure():
    """Get all infrastructure components"""
    return infrastructure_db

@app.get("/infrastructure/{infra_id}", response_model=Infrastructure)
async def get_infrastructure_item(infra_id: str):
    """Get specific infrastructure component by ID"""
    infra = next((i for i in infrastructure_db if i.id == infra_id), None)
    if not infra:
        raise HTTPException(status_code=404, detail="Infrastructure component not found")
    return infra

@app.put("/infrastructure/{infra_id}/status")
async def update_infrastructure_status(infra_id: str, status: str):
    """Update infrastructure status"""
    infra = next((i for i in infrastructure_db if i.id == infra_id), None)
    if not infra:
        raise HTTPException(status_code=404, detail="Infrastructure component not found")
    
    infra.status = status
    logger.info(f"Updated infrastructure {infra_id} status to {status}")
    return {"message": f"Infrastructure {infra_id} status updated to {status}"}

# Disruption endpoints
@app.get("/disruptions", response_model=List[Disruption])
async def get_disruptions():
    """Get all active disruptions"""
    return disruptions_db

@app.post("/disruptions", response_model=Disruption)
async def create_disruption(disruption: Disruption):
    """Report a new disruption"""
    disruptions_db.append(disruption)
    logger.warning(f"New disruption reported: {disruption.type} - {disruption.description}")
    return disruption

@app.put("/disruptions/{disruption_id}/resolve")
async def resolve_disruption(disruption_id: str):
    """Mark disruption as resolved"""
    disruption = next((d for d in disruptions_db if d.id == disruption_id), None)
    if not disruption:
        raise HTTPException(status_code=404, detail="Disruption not found")
    
    disruption.estimated_end_time = datetime.now()
    logger.info(f"Disruption {disruption_id} marked as resolved")
    return {"message": f"Disruption {disruption_id} resolved"}

# Optimization endpoint
@app.post("/optimize", response_model=OptimizationResponse)
async def optimize_schedule(request: OptimizationRequest, background_tasks: BackgroundTasks):
    """Optimize train schedule"""
    start_time = datetime.now()
    
    # Simulate optimization processing time
    await asyncio.sleep(random.uniform(0.5, 2.0))
    
    # Mock optimization results
    optimized_trains = []
    conflicts_resolved = random.randint(1, 5)
    total_delay_reduction = random.randint(10, 60)
    
    for train in request.trains:
        # Simulate some optimization
        optimized_train = train.copy()
        optimized_train.delay_minutes = max(0, train.delay_minutes - random.randint(5, 15))
        optimized_trains.append(optimized_train)
    
    optimization_time = (datetime.now() - start_time).total_seconds()
    
    response = OptimizationResponse(
        optimized_trains=optimized_trains,
        conflicts_resolved=conflicts_resolved,
        total_delay_reduction=total_delay_reduction,
        optimization_time=optimization_time,
        status="completed"
    )
    
    # Log optimization in background
    background_tasks.add_task(log_optimization, request, response)
    
    logger.info(f"Schedule optimization completed: {conflicts_resolved} conflicts resolved, {total_delay_reduction} minutes saved")
    return response

async def log_optimization(request: OptimizationRequest, response: OptimizationResponse):
    """Background task to log optimization results"""
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "trains_optimized": len(request.trains),
        "conflicts_resolved": response.conflicts_resolved,
        "delay_reduction": response.total_delay_reduction,
        "optimization_time": response.optimization_time
    }
    logger.info(f"Optimization logged: {log_entry}")

# Metrics endpoint for monitoring
@app.get("/metrics")
async def get_metrics():
    """Get system metrics for monitoring"""
    return {
        "timestamp": datetime.now().isoformat(),
        "trains": {
            "total": len(trains_db),
            "on_time": len([t for t in trains_db if t.delay_minutes == 0]),
            "delayed": len([t for t in trains_db if t.delay_minutes > 0]),
            "average_delay": sum(t.delay_minutes for t in trains_db) / len(trains_db) if trains_db else 0
        },
        "stations": {
            "total": len(stations_db),
            "operational": len([s for s in stations_db if s.status == "operational"]),
            "capacity_utilization": sum(s.current_trains / s.capacity for s in stations_db) / len(stations_db) if stations_db else 0
        },
        "infrastructure": {
            "total": len(infrastructure_db),
            "operational": len([i for i in infrastructure_db if i.status == "operational"]),
            "maintenance_due": len([i for i in infrastructure_db if i.maintenance_due and i.maintenance_due <= datetime.now() + timedelta(days=7)])
        },
        "disruptions": {
            "active": len(disruptions_db),
            "critical": len([d for d in disruptions_db if d.severity == "critical"]),
            "high": len([d for d in disruptions_db if d.severity == "high"])
        }
    }

# Error simulation endpoints for testing
@app.post("/simulate/error")
async def simulate_error():
    """Simulate an API error for testing"""
    raise HTTPException(status_code=500, detail="Simulated server error")

@app.post("/simulate/timeout")
async def simulate_timeout():
    """Simulate a timeout for testing"""
    await asyncio.sleep(15)  # Longer than typical timeout
    return {"message": "This should timeout"}

@app.post("/simulate/slow")
async def simulate_slow_response():
    """Simulate a slow response for latency testing"""
    await asyncio.sleep(random.uniform(2, 5))
    return {"message": "Slow response completed"}

# Scenario management endpoints
@app.get("/scenarios")
async def get_scenarios():
    """Get available scenarios"""
    scenarios = get_available_scenarios()
    return {
        "available_scenarios": scenarios,
        "current_scenario": current_scenario or "default",
        "scenario_count": len(scenarios)
    }

@app.post("/scenarios/{scenario_name}/load")
async def load_scenario(scenario_name: str):
    """Load a specific scenario"""
    available_scenarios = get_available_scenarios()
    
    if scenario_name not in available_scenarios and scenario_name != "default":
        raise HTTPException(status_code=404, detail=f"Scenario '{scenario_name}' not found")
    
    try:
        reload_sample_data(scenario_name if scenario_name != "default" else None)
        return {
            "message": f"Scenario '{scenario_name}' loaded successfully",
            "current_scenario": current_scenario or "default",
            "data_counts": {
                "trains": len(trains_db),
                "stations": len(stations_db),
                "infrastructure": len(infrastructure_db),
                "disruptions": len(disruptions_db)
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading scenario: {str(e)}")

@app.post("/reload")
async def reload_data_endpoint(scenario: Optional[str] = Query(None, description="Scenario to reload")):
    """Reload data from files"""
    try:
        reload_sample_data(scenario)
        return {
            "message": f"Data reloaded successfully{' for scenario: ' + scenario if scenario else ''}",
            "current_scenario": current_scenario or "default",
            "data_counts": {
                "trains": len(trains_db),
                "stations": len(stations_db),
                "infrastructure": len(infrastructure_db),
                "disruptions": len(disruptions_db)
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reloading data: {str(e)}")

@app.get("/data/summary")
async def get_data_summary():
    """Get summary of current data"""
    return {
        "current_scenario": current_scenario or "default",
        "data_counts": {
            "trains": len(trains_db),
            "stations": len(stations_db),
            "infrastructure": len(infrastructure_db),
            "disruptions": len(disruptions_db)
        },
        "train_types": list(set(train.train_type for train in trains_db if hasattr(train, 'train_type'))),
        "station_types": list(set(station.station_type for station in stations_db if hasattr(station, 'station_type'))),
        "infrastructure_types": list(set(infra.type for infra in infrastructure_db)),
        "disruption_types": list(set(disruption.type for disruption in disruptions_db))
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
