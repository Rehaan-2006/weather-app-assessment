from fastapi import FastAPI, Depends, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
import io
import csv

from app.database import Base, engine, get_db
from app import schemas, crud, services

# Generate Database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Weather Intelligence API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (GET, POST, PUT, DELETE)
    allow_headers=["*"],  # Allows all headers
)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"message": "An unexpected internal server error occurred. Please try again later."},
    )

@app.post("/api/weather", response_model=schemas.WeatherResponse, status_code=201)
async def create_weather(payload: schemas.WeatherCreate, db: Session = Depends(get_db)):
    # 1. Validate and resolve location via Geocoder
    geo = await services.geocode_location(payload.location)
    
    # 2. Fetch remote weather data
    weather_data = await services.fetch_weather(
        geo["latitude"], geo["longitude"], str(payload.start_date), str(payload.end_date)
    )
    
    # 3. Consolidate payload & Save to PostgreSQL
    db_payload = {
        "requested_location": payload.location,
        "resolved_location": geo["resolved_location"],
        "latitude": geo["latitude"],
        "longitude": geo["longitude"],
        "start_date": payload.start_date,
        "end_date": payload.end_date,
        "weather_data": weather_data
    }
    
    return crud.create_weather_log(db, db_payload)

@app.get("/api/weather/{log_id}/export")
def export_weather_log(log_id: int, format: str = "csv", db: Session = Depends(get_db)):
    log = crud.get_weather_log(db, log_id)
    if not log:
        raise HTTPException(status_code=404, detail="Record not found")
        
    if format.lower() == "csv":
        output = io.StringIO()
        writer = csv.writer(output)
        # Write headers
        writer.writerow(["ID", "Requested Location", "Resolved Location", "Start Date", "End Date"])
        writer.writerow([log.id, log.requested_location, log.resolved_location, log.start_date, log.end_date])
        
        return Response(
            content=output.getvalue(),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=weather_report_{log_id}.csv"}
        )
    
    # Fallback default JSON export
    return log

from app.config import settings # Assuming you handle API keys via config

@app.get("/api/weather", response_model=list[schemas.WeatherResponse])
def read_all_weather_logs(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    """READ (All) - Get historical logs with basic pagination."""
    return crud.get_all_weather_logs(db, skip=skip, limit=limit)


@app.get("/api/weather/{log_id}", response_model=schemas.WeatherResponse)
async def read_single_weather_log(log_id: int, db: Session = Depends(get_db)):
    """READ (Single) - Fetches db record and dynamically appends YouTube & Map points of interest."""
    log = crud.get_weather_log(db, log_id)
    if not log:
        raise HTTPException(status_code=404, detail="Weather log record not found")
    
    # Inject Phase 4 Third-Party features dynamically on Read
    videos = await services.fetch_youtube_videos(log.resolved_location, settings.YOUTUBE_API_KEY)
    map_link = services.generate_map_url(log.latitude, log.longitude)
    
    # Construct response mapping to schemas.WeatherResponse
    return {
        "id": log.id,
        "requested_location": log.requested_location,
        "resolved_location": log.resolved_location,
        "latitude": log.latitude,
        "longitude": log.longitude,
        "start_date": log.start_date,
        "end_date": log.end_date,
        "weather_data": log.weather_data,
        "youtube_videos": videos,
        "map_url": map_link
    }


@app.put("/api/weather/{log_id}", response_model=schemas.WeatherResponse)
async def update_weather(log_id: int, payload: schemas.WeatherCreate, db: Session = Depends(get_db)):
    """UPDATE - Re-validates input location/dates, pulls fresh API metrics, and updates row."""
    # 1. Verify existence of record first
    existing_log = crud.get_weather_log(db, log_id)
    if not existing_log:
        raise HTTPException(status_code=404, detail="Record code not found to update")
        
    # 2. Run validations and geocode the new parameters
    geo = await services.geocode_location(payload.location)
    weather_data = await services.fetch_weather(
        geo["latitude"], geo["longitude"], str(payload.start_date), str(payload.end_date)
    )
    
    updated_payload = {
        "requested_location": payload.location,
        "resolved_location": geo["resolved_location"],
        "latitude": geo["latitude"],
        "longitude": geo["longitude"],
        "start_date": payload.start_date,
        "end_date": payload.end_date,
        "weather_data": weather_data
    }
    
    updated_record = crud.update_weather_log(db, log_id, updated_payload)
    return updated_record


@app.delete("/api/weather/{log_id}", status_code=24)
def delete_weather(log_id: int, db: Session = Depends(get_db)):
    """DELETE - Permanently removes row log record from database."""
    success = crud.delete_weather_log(db, log_id)
    if not success:
        raise HTTPException(status_code=404, detail="Record not found")
    return Response(status_code=204)