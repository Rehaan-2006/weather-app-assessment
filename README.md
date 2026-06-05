# 🌤️ Weather App — Backend API

> **Tech Assessment #2 — Backend Engineering**
> Submitted as part of the PM Accelerator application process.

---

## 📌 About PM Accelerator

**Product Manager Accelerator Mission**

 By making industry-leading tools and education available to individuals from all backgrounds, we level the playing field for future PM leaders. This is the PM Accelerator motto, as we grant aspiring and experienced PMs what they need most – Access. We introduce you to industry leaders, surround you with the right PM ecosystem, and discover the new world of AI product management skills.

🔗 [www.pmaccelerator.io](https://www.pmaccelerator.io)

---

## 📊 Project Overview

A production-ready RESTful API that lets users store, query, and export
historical weather data for any location in the world. Built with FastAPI and
PostgreSQL, it covers all CRUD requirements and enriches responses with
third-party data from YouTube and OpenStreetMap.

**Highlights:**
- Accept any location format — city name, ZIP code, GPS coordinates, or landmark
- Fuzzy geocoding resolves vague inputs (e.g. "Eiffel Tower") to exact coordinates
- Full CRUD with strict Pydantic validation on all inputs
- Dynamic API enrichment: YouTube travel videos + OpenStreetMap links per location
- One-click CSV and JSON export of any stored weather record
- Auto-generated Swagger UI for testing all endpoints

---

## 🗂️ Project Structure

```text
weather-app-assessment/
├── app/
│   ├── main.py          # FastAPI app, CORS, error handling, and all route endpoints
│   ├── models.py        # SQLAlchemy ORM table definitions
│   ├── schemas.py       # Pydantic request/response models + date range validation
│   ├── services.py      # External API calls: Nominatim, Open-Meteo, YouTube
│   ├── crud.py          # Database CRUD operations
│   ├── config.py        # Pydantic settings for environment variables
│   └── database.py      # PostgreSQL connection + session management
├── .env.example         # Template for required environment variables
├── .gitignore
├── requirements.txt
└── README.md
```

---

## ⚙️ Local Setup

### 1. Clone the repository
```bash
git clone https://github.com/Rehaan-2006/weather-app-assessment.git
cd weather-app-assessment
```

### 2. Create and activate a virtual environment
```bash
python3 -m venv .venv
source .venv/bin/activate        # macOS / Linux
# .venv\Scripts\activate         # Windows
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure environment variables
Copy the example file and fill in your credentials:
```bash
cp .env.example .env
```

Edit `.env`:
```env
# PostgreSQL connection string
DATABASE_URL=postgresql://user:password@localhost:5432/weather_db

# Google Cloud API key with YouTube Data API v3 enabled
YOUTUBE_API_KEY=your_key_here

ENVIRONMENT=development
PORT=8000
```

> **YouTube API key:** Create one free at [console.cloud.google.com](https://console.cloud.google.com) →
> enable "YouTube Data API v3" → Credentials → Create API Key.

### 5. Start the server
```bash
uvicorn app.main:app --reload
```

Database tables are created automatically on first boot via SQLAlchemy.

### 6. Open Swagger UI
```http://127.0.0.1:8000/docs```
All endpoints are testable directly from the browser — no Postman needed.

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Root — returns author info + PM Accelerator description |
| `POST` | `/api/weather` | Create a weather log for a location + date range |
| `GET` | `/api/weather` | List all stored weather logs (supports pagination) |
| `GET` | `/api/weather/{id}` | Get one record, dynamically enriched with YouTube + OpenStreetMap |
| `PUT` | `/api/weather/{id}` | Update an existing weather record |
| `DELETE` | `/api/weather/{id}` | Delete a weather record |
| `GET` | `/api/weather/{id}/export` | Export record as a downloadable CSV or JSON |

---

## 🔬 How It Works

### Location Resolution
Every request passes through Nominatim (OpenStreetMap's free geocoder).
Input can be anything — `"Tokyo"`, `"90210"`, `"Eiffel Tower"`, `"-33.8688, 151.2093"`.
Nominatim resolves it to a verified lat/lon pair, which is stored with the record.
If the location cannot be resolved, the API returns a clean `400` validation error.

### Date Range Validation
Handled in the Pydantic schema layer before the request reaches the database.
Rules enforced: `start_date` must be before `end_date`, and both must be valid
calendar dates.

### Weather Data
Historical temperature and weather data is fetched from
[Open-Meteo](https://open-meteo.com/) — a free, no-key API.
Data is stored per record in the PostgreSQL database.

> **Note:** As an archive API, requesting future dates will return a `502` error.

### API Enrichment (READ endpoint)
When fetching a record by ID, the response is dynamically enriched with:
- **YouTube:** Top 3 travel videos for the location via YouTube Data API v3
- **OpenStreetMap:** Direct map URL centered on the stored coordinates

### Data Export
The export endpoint serializes the stored record into a properly formatted file
and returns it as a file download (`Content-Disposition: attachment`).
Supports both CSV and JSON formats.

---

## 🧰 Tech Stack

| Layer | Technology |
|-------|------------|
| Framework | FastAPI (Python) |
| Database | PostgreSQL |
| ORM | SQLAlchemy |
| Validation | Pydantic |
| Geocoding | Nominatim / OpenStreetMap |
| Weather Data | Open-Meteo API |
| Media Enrichment | YouTube Data API v3 |
| Server | Uvicorn |

---

## 📦 Dependencies

See `requirements.txt`. Key packages: 
fastapi
uvicorn
sqlalchemy
psycopg2-binary
pydantic
pydantic-settings
httpx
alembic

---

## 🎥 Demo Video

🔗 ([Youtube Link here](https://drive.google.com/file/d/1NUQonjc6YQuj0dGrGU12feQWnWnn1D3F/view?usp=sharing\))

---

*Submitted by Rehaan | PM Accelerator Tech Assessment #2*