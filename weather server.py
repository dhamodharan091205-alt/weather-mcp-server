from mcp.server.fastmcp import FastMCP
import httpx

mcp = FastMCP("Weather Checker")

# Free API - No API key needed!
async def get_coords(city: str):
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1"
        )
        data = resp.json()
        if not data.get("results"):
            return None
        place = data["results"][0]
        return place["latitude"], place["longitude"], place["name"], place["country"]

@mcp.tool()
async def get_weather(city: str) -> str:
    """Get current weather for any city. Input: city name like 'Chennai' or 'London'"""
    coords = await get_coords(city)
    if not coords:
        return f"City '{city}' not found."

    lat, lon, name, country = coords

    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
        )
        weather = resp.json()["current_weather"]

        return f"""
Weather in {name}, {country}:
🌡️ Temperature: {weather['temperature']}°C
💨 Wind Speed: {weather['windspeed']} km/h
🕒 Time: {weather['time']}
Condition Code: {weather['weathercode']}
"""

@mcp.tool()
async def get_forecast(city: str) -> str:
    """Get 3-day forecast for a city"""
    coords = await get_coords(city)
    if not coords:
        return f"City '{city}' not found."
    lat, lon, name, country = coords

    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&daily=temperature_2m_max,temperature_2m_min&timezone=auto"
        )
        daily = resp.json()["daily"]
        result = f"3-Day Forecast for {name}, {country}:\n"
        for i in range(3):
            result += f"{daily['time'][i]}: Max {daily['temperature_2m_max'][i]}°C, Min {daily['temperature_2m_min'][i]}°C\n"
        return result

if __name__ == "__main__":
    mcp.run()