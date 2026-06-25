# SPDX-License-Identifier: AGPL-3.0-or-later

"""
Weather Search Engine for Atomic Search
Provides instant weather information in search results
"""

import json
import re
from datetime import datetime
from typing import List, Dict, Any, Optional

about = {
    "name": "Weather",
    "description": "Get current weather and forecasts",
    "instances": ["built-in"],
    "self-hosted": True,
    "website": "https://atomicsearch.dev",
}

# WeatherAPI.com free tier (or use wttr.in as fallback)
WEATHER_API_URL = "https://api.weatherapi.com/v1"
WEATHER_CACHE_SECONDS = 600  # 10 minutes


def init(_engine_settings: Dict[str, Any]) -> None:
    """Initialize weather engine with API key if available"""
    pass


def request(query: str, params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Build weather API request
    
    Extracts location from query and builds API request
    """
    # Check if this is a weather query
    weather_patterns = [
        r'^weather\s+(?:in|for|at)?\s*(.+)$',
        r'^how(?:\'s| is) the weather\s+(?:in|for|at)?\s*(.+)$',
        r'^what(?:\'s| is) the weather\s+(?:in|for|at)?\s*(.+)$',
        r'^(.+?)\s+weather$',
    ]
    
    query_lower = query.lower().strip()
    location = None
    
    for pattern in weather_patterns:
        match = re.match(pattern, query_lower, re.IGNORECASE)
        if match:
            location = match.group(1).strip()
            break
    
    if not location:
        # Default to IP-based geolocation
        location = "auto:ip"
    
    params["url"] = f"{WEATHER_API_URL}/current.json"
    params["query_params"] = {
        "q": location,
        "aqi": "no",
        "alerts": "no"
    }
    params["soft_max_redirects"] = 3
    
    return params


def response(resp_search: Dict[str, Any], resp_one: Any) -> List[Dict[str, Any]]:
    """
    Parse weather API response and format results
    
    Returns instant answer card format
    """
    try:
        data = json.loads(resp_one.text)
        
        if "error" in data:
            return []
        
        location = data.get("location", {})
        current = data.get("current", {})
        condition = current.get("condition", {})
        
        # Build instant answer
        result = {
            "answer": _format_weather_card(data),
            "url": f"https://www.weatherapi.com/weather?q={location.get('name', '')}",
            "title": f"Weather in {location.get('name', 'Unknown')}",
            "engine": "weather",
            "is_weather": True,
            "template": "weather.html",
            # Raw data for template
            "weather_data": {
                "location": {
                    "name": location.get("name", ""),
                    "region": location.get("region", ""),
                    "country": location.get("country", ""),
                    "localtime": location.get("localtime", ""),
                    "tz_id": location.get("tz_id", ""),
                },
                "current": {
                    "temp_c": current.get("temp_c", 0),
                    "temp_f": current.get("temp_f", 0),
                    "condition_text": condition.get("text", ""),
                    "condition_icon": condition.get("icon", ""),
                    "condition_code": condition.get("code", 0),
                    "wind_kph": current.get("wind_kph", 0),
                    "wind_mph": current.get("wind_mph", 0),
                    "wind_dir": current.get("wind_dir", ""),
                    "humidity": current.get("humidity", 0),
                    "cloud": current.get("cloud", 0),
                    "feelslike_c": current.get("feelslike_c", 0),
                    "feelslike_f": current.get("feelslike_f", 0),
                    "uv": current.get("uv", 0),
                    "vis_km": current.get("vis_km", 0),
                    "gust_kph": current.get("gust_kph", 0),
                },
                "forecast": _get_simple_forecast(current),
            }
        }
        
        return [result]
    
    except Exception:
        return []


def _format_weather_card(data: Dict[str, Any]) -> str:
    """
    Format weather data as a readable card
    """
    location = data.get("location", {})
    current = data.get("current", {})
    condition = current.get("condition", {})
    
    temp_c = current.get("temp_c", 0)
    feelslike_c = current.get("feelslike_c", 0)
    humidity = current.get("humidity", 0)
    wind_kph = current.get("wind_kph", 0)
    wind_dir = current.get("wind_dir", "")
    uv = current.get("uv", 0)
    
    card = f"""
**{location.get('name', 'Unknown')}, {location.get('country', '')}**

🌡️ **{temp_c:.0f}°C** ({condition.get('text', '')})
💨 Feels like: {feelslike_c:.0f}°C
💧 Humidity: {humidity}%
🌬️ Wind: {wind_kph:.0f} km/h {wind_dir}
☀️ UV Index: {uv}
"""
    return card.strip()


def _get_simple_forecast(current: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract simplified forecast info from current conditions
    """
    return {
        "suggestion": _get_weather_suggestion(
            current.get("temp_c", 20),
            current.get("humidity", 50),
            current.get("uv", 0),
            current.get("cloud", 0),
            current.get("condition", {}).get("code", 0)
        )
    }


def _get_weather_suggestion(temp: float, humidity: int, uv: float, cloud: int, code: int) -> str:
    """
    Generate weather-based activity suggestion
    """
    suggestions = []
    
    # Temperature-based
    if temp < 5:
        suggestions.append("🧥 Very cold - dress warmly!")
    elif temp < 15:
        suggestions.append("🧶 Cool - layered clothing recommended")
    elif temp < 25:
        suggestions.append("👕 Pleasant temperature")
    elif temp < 30:
        suggestions.append("🩱 Warm - stay hydrated")
    else:
        suggestions.append("🥵 Hot - avoid prolonged sun exposure")
    
    # UV-based
    if uv >= 8:
        suggestions.append("🧴 Very high UV - avoid sun")
    elif uv >= 6:
        suggestions.append("☂️ High UV - sunscreen recommended")
    elif uv >= 3:
        suggestions.append("🌂 Moderate UV")
    
    # Rain codes (1000-1009 typically mean clear/cloudy, higher = rain)
    if code >= 1063:
        suggestions.append("🌧️ Precipitation possible")
    
    return " | ".join(suggestions[:3])


# wttr.in fallback (no API key required)
def _wttr_request(query: str, params: Dict[str, Any]) -> Dict[str, Any]:
    """Fallback to wttr.in if WeatherAPI unavailable"""
    query_clean = re.sub(r'^(?:weather\s+)?(?:in|for|at)?\s*', '', query, flags=re.IGNORECASE).strip()
    
    if not query_clean:
        query_clean = "~"
    
    params["url"] = f"https://wttr.in/{urllib.parse.quote(query_clean)}.json"
    params["soft_max_redirects"] = 3
    
    return params


# Export for use in other modules
__all__ = ['request', 'response', 'init', 'about']
