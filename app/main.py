import json

from fastapi import FastAPI, Depends, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
import io
import csv

from app.config import settings 
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

@app.get("/")
def root():
    return {
        "author": "Shaikh Mohd Rehaan",
        "about_pm_accelerator": (
            "Product Manager Accelerator(PMA) "
            "From entry-level to VP of Product, we support PM professionals through every stage of their careers."
            "Through mentorship, real-world projects, and a strong community, PMA helps "
            "members land jobs at leading tech companies. Learn more at "
            "https://www.linkedin.com/school/pmaccelerator/"
        ),
        "app": "Weather Intelligence API — Tech Assessment #2",
        "docs": "/docs",
    }

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
    """
    EXPORT - Download a single weather log in your chosen format.
    Supported values for ?format=  →  csv | json | xml | markdown
    """
    log = crud.get_weather_log(db, log_id)
    if not log:
        raise HTTPException(status_code=404, detail="Record not found")

    #CSV
    if format.lower() == "csv":
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow([
            "ID", "Requested Location", "Resolved Location",
            "Latitude", "Longitude", "Start Date", "End Date", "Weather Data"
        ])
        writer.writerow([
            log.id, log.requested_location, log.resolved_location,
            log.latitude, log.longitude, log.start_date, log.end_date,
            json.dumps(log.weather_data)
        ])
        return Response(
            content=output.getvalue(),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=weather_report_{log_id}.csv"},
        )

    #JSON
    elif format.lower() == "json":                    
        data = {
            "id": log.id,
            "requested_location": log.requested_location,
            "resolved_location": log.resolved_location,
            "latitude": log.latitude,
            "longitude": log.longitude,
            "start_date": str(log.start_date),
            "end_date": str(log.end_date),
            "weather_data": log.weather_data,
        }
        return Response(
            content=json.dumps(data, indent=2),
            media_type="application/json",
            headers={"Content-Disposition": f"attachment; filename=weather_report_{log_id}.json"},
        )

    #XML
    elif format.lower() == "xml":                      
        root_el = ET.Element("WeatherLog")
        ET.SubElement(root_el, "ID").text = str(log.id)
        ET.SubElement(root_el, "RequestedLocation").text = log.requested_location
        ET.SubElement(root_el, "ResolvedLocation").text = log.resolved_location
        ET.SubElement(root_el, "Latitude").text = str(log.latitude)
        ET.SubElement(root_el, "Longitude").text = str(log.longitude)
        ET.SubElement(root_el, "StartDate").text = str(log.start_date)
        ET.SubElement(root_el, "EndDate").text = str(log.end_date)
        ET.SubElement(root_el, "WeatherData").text = json.dumps(log.weather_data)
        xml_str = '<?xml version="1.0" encoding="UTF-8"?>\n' + ET.tostring(root_el, encoding="unicode")
        return Response(
            content=xml_str,
            media_type="application/xml",
            headers={"Content-Disposition": f"attachment; filename=weather_report_{log_id}.xml"},
        )

    #MARKDOWN 
    elif format.lower() == "markdown":                 
        md = f"""# Weather Report — Log #{log.id}

**Requested Location:** {log.requested_location}
**Resolved Location:** {log.resolved_location}
**Coordinates:** {log.latitude}, {log.longitude}
**Date Range:** {log.start_date} → {log.end_date}

## Weather Data
```json
{json.dumps(log.weather_data, indent=2)}
```
"""
        return Response(
            content=md,
            media_type="text/markdown",
            headers={"Content-Disposition": f"attachment; filename=weather_report_{log_id}.md"},
        )

    #Unknown format 
    else:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported format '{format}'. Choose from: csv, json, xml, markdown",
        )


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


@app.delete("/api/weather/{log_id}", status_code=204)
def delete_weather(log_id: int, db: Session = Depends(get_db)):
    """DELETE - Permanently removes row log record from database."""
    success = crud.delete_weather_log(db, log_id)
    if not success:
        raise HTTPException(status_code=404, detail="Record not found")
    return Response(status_code=204)