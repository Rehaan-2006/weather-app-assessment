from pydantic import BaseModel, model_validator
from datetime import date
from typing import Any, Optional

class WeatherCreate(BaseModel):
    location: str
    start_date: date
    end_date: date

    @model_validator(mode="after")
    def validate_dates(self) -> "WeatherCreate":
        if self.end_date < self.start_date:
            raise ValueError("end_date cannot be earlier than start_date")
        return self

class WeatherResponse(BaseModel):
    id: int
    requested_location: str
    resolved_location: str
    latitude: float
    longitude: float
    start_date: date
    end_date: date
    weather_data: Any
    youtube_videos: Optional[list] = []
    map_url: Optional[str] = None

    class Config:
        from_attributes = True