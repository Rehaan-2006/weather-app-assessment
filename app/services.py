import httpx
from fastapi import HTTPException

async def geocode_location(location: str) -> dict:
    """
    Validates if location exists using OpenStreetMap Nominatim API (Fuzzy Match).
    Returns dict with resolved_name, lat, lon.
    """
    url = f"https://nominatim.openstreetmap.org/search?q={location}&format=json&limit=1"
    headers = {"User-Agent": "WeatherAppAssessment/1.0"}
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        data = response.json()
        
        if not data:
            raise HTTPException(status_code=400, detail=f"Location '{location}' could not be verified.")
        
        return {
            "resolved_location": data[0]["display_name"],
            "latitude": float(data[0]["lat"]),
            "longitude": float(data[0]["lon"])
        }

async def fetch_weather(lat: float, lon: float, start_date: str, end_date: str) -> dict:
    """Fetches historical/forecast weather data using Open-Meteo API."""
    url = f"https://archive-api.open-meteo.com/v1/archive?latitude={lat}&longitude={lon}&start_date={start_date}&end_date={end_date}&daily=temperature_2m_max,temperature_2m_min&timezone=auto"
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        if response.status_code != 200:
            raise HTTPException(status_code=502, detail="Weather provider service is temporarily unavailable.")
        return response.json()


async def fetch_youtube_videos(location_name: str, api_key: str) -> list:
    """
    Fetches the top 3 YouTube video titles and links for a resolved location.
    Costs 100 quota units per call. Falls back to an empty list gracefully on failure.
    """
    if not api_key:
        return []
        
    url = "https://www.googleapis.com/youtube/v3/search"
    params = {
        "part": "snippet",
        "q": f"Travel guide {location_name}",
        "maxResults": 3,
        "type": "video",
        "key": api_key
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, params=params)
            if response.status_code == 200:
                data = response.json()
                videos = []
                for item in data.get("items", []):
                    video_id = item["id"]["videoId"]
                    snippet = item["snippet"]
                    videos.append({
                        "title": snippet["title"],
                        "url": f"https://www.youtube.com/watch?v={video_id}",
                        "thumbnail": snippet["thumbnails"]["default"]["url"]
                    })
                return videos
        except Exception:
            # Prevent third-party API issues from crashing our core application
            return []
    return []

def generate_map_url(latitude: float, longitude: float) -> str:
    """Generates an open-source shareable OpenStreetMap view link based on coordinates."""
    return f"https://www.openstreetmap.org/?mlat={latitude}&mlon={longitude}#map=13/{latitude}/{longitude}"