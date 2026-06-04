# Tech Assessment: Weather App Backend

A robust, production-ready RESTful API built with **FastAPI** and **PostgreSQL**. This service allows users to track, store, and export historical and forecasted weather data alongside curated points of interest and media.

## Features
* **Full CRUD Functionality:** Create, Read, Update, and Delete location-based weather logs.
* **Fuzzy Geocoding:** Automatically resolves standard text (e.g., "Eiffel Tower", "90210") into exact GPS coordinates using Nominatim OpenStreetMap.
* **Date Range Validation:** Strict input validation utilizing Pydantic.
* **API Mashups (Phase 4):** Dynamically enriches location queries with YouTube travel videos (YouTube Data API v3) and OpenStreetMap URLs.
* **Data Export:** Native functionality to export database rows into a downloadable `.csv` format.

## Tech Stack
* **Framework:** FastAPI (Python)
* **Database:** PostgreSQL (via SQLAlchemy ORM)
* **Validation:** Pydantic
* **Migrations:** Alembic (Optional layout included)

---

## Local Setup Instructions

### 1. Clone the repository
\`\`\`bash
git clone https://github.com/YOUR_USERNAME/weather-app-assessment.git
cd weather-app-assessment
\`\`\`

### 2. Set up the Virtual Environment & Dependencies
\`\`\`bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows use `venv\Scripts\activate`
pip install -r requirements.txt
\`\`\`

### 3. Environment Variables
Create a `.env` file in the root directory. You can duplicate the provided `.env.example` file.
\`\`\`env
# Database Connection (Local or Cloud PostgreSQL)
DATABASE_URL=postgresql://user:password@localhost:5432/weather_db

# Required for media enrichment (Free Tier)
YOUTUBE_API_KEY=your_google_cloud_api_key_here

ENVIRONMENT=development
PORT=8000
\`\`\`

### 4. Run the Application
Start the uvicorn server. The database tables will generate automatically on boot.
\`\`\`bash
uvicorn app.main:app --reload
\`\`\`

### 5. View Documentation & Test
Once the server is running, navigate to the auto-generated Swagger UI to test all endpoints:
👉 **[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)**