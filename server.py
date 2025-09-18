from typing import Any
import json
import logging
import httpx
from mcp.server.fastmcp import FastMCP

# Constants
WEATHER_OPENMETEO_API_BASE = "https://api.open-meteo.com/v1"
GEOCODING_OPENMATEO_API_BASE = "https://geocoding-api.open-meteo.com/v1"
USER_AGENT = "weather-app/1.0"

# Initialize FastMCP server
mcp = FastMCP("weather")
logger = logging.getLogger(__name__)

# Helper function to make a request to the Open-Meteo API
async def make_openmeteo_request(url: str) -> dict[str, Any] | None:
    """Make a request to the Open-Meteo API with proper error handling."""
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "application/json"
    }
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, timeout=30.0)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error("Open-Meteo request failed: %s", e)
            return None
        
@mcp.tool()
async def get_current_weather(latitude: float, longitude: float) -> str:
    """Get current weather for a location.

    Args:
        latitude: Latitude of the location
        longitude: Longitude of the location
    """
    
    url = f"{WEATHER_OPENMETEO_API_BASE}/forecast?latitude={latitude}&longitude={longitude}&current=temperature_2m,is_day,showers,cloud_cover,wind_speed_10m,wind_direction_10m,pressure_msl,snowfall,precipitation,relative_humidity_2m,apparent_temperature,rain,weather_code,surface_pressure,wind_gusts_10m"
    
    data = await make_openmeteo_request(url)

    if not data:
        return "Unable to fetch current weather data for this location."

    return json.dumps(data)

@mcp.tool()
async def get_forecast(latitude: float, longitude: float, days: int = 7) -> str:
    """Get forecasted weather for a location.

    Args:
        latitude: Latitude of the location
        longitude: Longitude of the location
        days: Days in the future
    """
    
    url = f"{WEATHER_OPENMETEO_API_BASE}/forecast?latitude={latitude}&longitude={longitude}&forecast_days={days}&daily=temperature_2m_max,temperature_2m_min,precipitation_sum,rain_sum,snowfall_sum,wind_speed_10m_max,wind_gusts_10m_max,wind_direction_10m_dominant,weathercode,sunrise,sunset&timezone=auto"
    
    data = await make_openmeteo_request(url)

    if not data:
        return "Unable to fetch forecasted weather data for this location."

    return json.dumps(data)

@mcp.tool()
async def get_location(search_term: str, count: int = 10):
    """Search for location.

    Args:
        search_term: String to search for, city, country, etc
        count: Number of search results to return
    """
    
    url = f"{GEOCODING_OPENMATEO_API_BASE}/search?name={search_term}&count={count}"
    
    data = await make_openmeteo_request(url)

    if not data:
        return f"Unable to fetch location data for {search_term}"

    return json.dumps(data)

if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='stdio')