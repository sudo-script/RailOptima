"""
RailOptima API - Integrated with Next.js frontend
This is a copy of the main API with CORS configured for same-domain deployment
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks, Query
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import random
import pandas as pd
import asyncio
import logging
import os
import sys

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="RailOptima API",
    description="Railway traffic management and optimization API",
    version="1.0.0"
)

# Add CORS middleware - configured for same domain
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://<YOUR-VERCEL-PROJECT>.vercel.app",   # add this
        "http://localhost:3000",
        "http://localhost:9002",
        "https://sihh.netlify.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class Train(BaseModel):
    id: str
    name: str
    route: str
    departure_time: str
    arrival_time: str
    status: str = "scheduled"
    priority: int = Field(ge=1, le=5, description="Priority level 1-5")
    capacity: int = Field(gt=0, description="Passenger capacity")
    current_station: Optional[str] = None
    delay_minutes: int = 0
    progress: int = 0
    passengers: int = 0
    nextStop: str = "Next Station"

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
    maintenance_due: Optional[str] = None
    capacity: Optional[int] = None

class Disruption(BaseModel):
    id: str
    type: str  # "delay", "cancellation", "track_closure", "signal_failure"
    severity: str  # "low", "medium", "high", "critical"
    affected_trains: List[str]
    affected_stations: List[str]
    start_time: str
    estimated_end_time: Optional[str] = None
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

def load_trains_from_csv() -> List[Dict[str, Any]]:
    try:
        csv_path = os.path.join(os.path.dirname(__file__), "..", "..", "Audit", "TestData", "human_decision_schedule.csv")
        if not os.path.exists(csv_path):
            logger.error(f"CSV file not found at {csv_path}")
            return []

        df = pd.read_csv(csv_path)
        today = datetime.now().date()
        trains = []

        for _, row in df.iterrows():
            # Times
            departure_time = datetime.combine(today, datetime.strptime(row["scheduled_departure"], "%H:%M").time())
            arrival_time = datetime.combine(today, datetime.strptime(row["optimized_departure"], "%H:%M").time())

            # Delay & status
            delay = int(row["delay_min"])
            if delay == 0:
                status = "On Time"
            elif delay < 15:
                status = "At Risk"
            else:
                status = f"Delayed ({delay} min)"

            # Progress = how much of journey completed (mocked for now)
            total_journey = (arrival_time - departure_time).total_seconds()
            elapsed = (datetime.now() - departure_time).total_seconds()
            progress = max(0, min(100, int((elapsed / total_journey) * 100))) if total_journey > 0 else 0

            trains.append({
                "id": str(row["train_id"]),
                "name": f"Train {row['train_id']}",
                "route": f"Station A → Station B",   # TODO: real start/end from your data
                "departure_time": departure_time.isoformat(),
                "arrival_time": arrival_time.isoformat(),
                "status": status,
                "priority": int(row["priority"]),
                "capacity": 500,
                "delay_minutes": delay,
                "progress": progress,
                "passengers": random.randint(100, 400),
                "nextStop": f"S{random.randint(1, 5):03d}",
                "current_station": f"S{random.randint(1, 5):03d}"
            })

        return trains
    except Exception as e:
        logger.error(f"Error loading CSV trains: {e}")
        return []

def load_conflict_report_data() -> List[Dict[str, Any]]:
    """Load data from conflict_report.csv for KPI calculations"""
    try:
        csv_path = os.path.join(os.path.dirname(__file__), "..", "..", "optimizer", "conflict_report.csv")
        if not os.path.exists(csv_path):
            logger.error(f"Conflict report CSV file not found at {csv_path}")
            return []

        df = pd.read_csv(csv_path)
        return df.to_dict('records')
    except Exception as e:
        logger.error(f"Error loading conflict report data: {e}")
        return []


# Mock data storage - using the same data as your frontend
trains_db: List[Train] = [
    Train(
        id="12951",
        name="Rajdhani Express",
        route="Mumbai Central to New Delhi",
        departure_time=(datetime.now() + timedelta(hours=2)).isoformat(),
        arrival_time=(datetime.now() + timedelta(hours=8)).isoformat(),
        status="On Time",
        priority=5,
        capacity=750,
        current_station="Surat",
        delay_minutes=0,
        progress=25,
        passengers=650,
        nextStop="Vadodara"
    ),
    Train(
        id="22439",
        name="Shatabdi Express",
        route="New Delhi to Katra",
        departure_time=(datetime.now() + timedelta(hours=1)).isoformat(),
        arrival_time=(datetime.now() + timedelta(hours=6)).isoformat(),
        status="At Risk",
        priority=4,
        capacity=600,
        current_station="Ambala Cantt",
        delay_minutes=10,
        progress=40,
        passengers=580,
        nextStop="Jammu Tawi"
    ),
    Train(
        id="12301",
        name="Howrah Rajdhani",
        route="Howrah to New Delhi",
        departure_time=(datetime.now() - timedelta(hours=1)).isoformat(),
        arrival_time=(datetime.now() + timedelta(hours=5)).isoformat(),
        status="Delayed",
        priority=5,
        capacity=820,
        current_station="Mughalsarai",
        delay_minutes=45,
        progress=60,
        passengers=750,
        nextStop="Allahabad"
    ),
    Train(
        id="12002",
        name="Bhopal Express",
        route="New Delhi to Bhopal",
        departure_time=(datetime.now() + timedelta(hours=3)).isoformat(),
        arrival_time=(datetime.now() + timedelta(hours=9)).isoformat(),
        status="On Time",
        priority=3,
        capacity=550,
        current_station="Agra Cantt",
        delay_minutes=0,
        progress=15,
        passengers=480,
        nextStop="Gwalior"
    )
]

stations_db: List[Station] = [
    Station(id="MUM", name="Mumbai Central", location={"lat": 19.0176, "lng": 72.8562}, capacity=20, current_trains=5),
    Station(id="DEL", name="New Delhi", location={"lat": 28.6448, "lng": 77.2167}, capacity=25, current_trains=8),
    Station(id="HWH", name="Howrah", location={"lat": 22.5851, "lng": 88.3468}, capacity=15, current_trains=3),
    Station(id="BPL", name="Bhopal", location={"lat": 23.2599, "lng": 77.4126}, capacity=12, current_trains=2),
]

disruptions_db: List[Disruption] = [
    Disruption(
        id="D001",
        type="Signal Failure",
        severity="High",
        affected_trains=["12301", "22439"],
        affected_stations=["GZB"],
        start_time=(datetime.now() - timedelta(minutes=30)).isoformat(),
        estimated_end_time=(datetime.now() + timedelta(minutes=45)).isoformat(),
        description="Complete signal failure on lines 3 and 4. RRI team dispatched. ETA 45 mins."
    ),
    Disruption(
        id="D002",
        type="Track Blockage",
        severity="Medium",
        affected_trains=["12301"],
        affected_stations=["ASN"],
        start_time=(datetime.now() - timedelta(minutes=15)).isoformat(),
        estimated_end_time=(datetime.now() + timedelta(minutes=30)).isoformat(),
        description="Debris on track due to local construction work. Line clearing in progress."
    ),
    Disruption(
        id="D003",
        type="Passenger Incident",
        severity="Low",
        affected_trains=["12951"],
        affected_stations=["NGP"],
        start_time=(datetime.now() - timedelta(minutes=5)).isoformat(),
        estimated_end_time=(datetime.now() + timedelta(minutes=20)).isoformat(),
        description="Medical emergency reported in coach S5. Awaiting paramedic team."
    )
]

# API Endpoints
@app.get("/")
async def root():
    """API root endpoint"""
    return {"message": "RailOptima API is running", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "uptime": "operational"
    }

# Train endpoints
@app.get("/trains", response_model=List[Train])
async def get_trains():
    """Get all trains"""
    return trains_db

@app.get("/trains/csv")
async def get_csv_trains():
    """Get train data from human_decision_schedule.csv"""
    try:
        # Path to the CSV file
        csv_path = os.path.join(os.path.dirname(__file__), '..', '..', 'Audit', 'TestData', 'human_decision_schedule.csv')
        
        if not os.path.exists(csv_path):
            raise HTTPException(status_code=404, detail="CSV file not found")
        
        # Read CSV data
        df = pd.read_csv(csv_path)
        
        # Convert to API format
        trains = []
        for _, row in df.iterrows():
            # Determine status based on current time and schedule
            current_time = datetime.now().time()
            scheduled_time = datetime.strptime(row['scheduled_departure'], '%H:%M').time()
            optimized_time = datetime.strptime(row['optimized_departure'], '%H:%M').time()
            
            # Simple status logic based on time
            if current_time < scheduled_time:
                status = "scheduled"
            elif current_time < optimized_time:
                status = "departed"
            else:
                status = "arrived"
            
            train = {
                "id": row['train_id'],
                "name": f"Train {row['train_id']}",
                "route": f"Route {row['train_id']}",  # You can customize this
                "departure_time": f"2025-09-13T{row['scheduled_departure']}:00",
                "arrival_time": f"2025-09-13T{row['optimized_departure']}:00",
                "status": status,
                "priority": int(row['priority']),
                "capacity": random.randint(200, 500),  # Random capacity
                "current_station": f"S{random.randint(1, 5):03d}",  # Random station
                "delay_minutes": int(row['delay_min']),
                "progress": random.randint(0, 100),  # Random progress
                "passengers": random.randint(100, 400),  # Random passengers
                "nextStop": f"S{random.randint(1, 5):03d}",  # Random next stop
            }
            trains.append(train)
        
        return trains
        
    except Exception as e:
        logger.error(f"Error loading CSV data: {e}")
        raise HTTPException(status_code=500, detail=f"Error loading CSV data: {str(e)}")

@app.get("/trains/{train_id}", response_model=Train)
async def get_train(train_id: str):
    """Get specific train by ID"""
    train = next((t for t in trains_db if t.id == train_id), None)
    if not train:
        raise HTTPException(status_code=404, detail="Train not found")
    return train

# Station endpoints
@app.get("/stations", response_model=List[Station])
async def get_stations():
    """Get all stations"""
    return stations_db

# KPI endpoints
@app.get("/kpi")
async def get_kpi_data():
    """Get KPI data for dashboard"""
    # Use conflict report data for avg delay
    conflict_data = load_conflict_report_data()
    avg_delay = sum(t["delay_minutes"] for t in conflict_data) / len(conflict_data) if conflict_data else 0
    
    # Use human_decision_schedule.csv for punctuality and decrease by 5%
    csv_trains = load_trains_from_csv()
    total_trains = len(csv_trains)
    on_time_trains = len([t for t in csv_trains if t["delay_minutes"] == 0])
    punctuality = (on_time_trains / total_trains * 100) if total_trains > 0 else 0
    # Decrease punctuality by 5%
    punctuality = max(0, punctuality - 5)
    
    return {
        "punctuality": {
            "value": round(punctuality, 1),
            "target": 95.0,
            "trend": -0.5
        },
        "avgDelay": {
            "value": round(avg_delay, 1),
            "target": "<5 min",
            "trend": 1.2
        },
        "activeTrains": {
            "value": total_trains,
            "capacity": 600,
            "trend": 12
        },
        "disruptions": {
            "value": len(disruptions_db),
            "last24h": 25,
            "trend": 2
        }
    }

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
    
    logger.info(f"Schedule optimization completed: {conflicts_resolved} conflicts resolved, {total_delay_reduction} minutes saved")
    return response

if __name__ == "__main__":
    import uvicorn, os
    uvicorn.run(app,
                host="0.0.0.0",
                port=int(os.getenv("PORT", "8000")),
                log_level="info")

