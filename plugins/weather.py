import requests
import re
from advanced_plugin_manager import BasePlugin

class WeatherPlugin(BasePlugin):
    def __init__(self):
        super().__init__()
        self.description = "Get weather information for any city"
        self.commands = ["weather", "temperature", "forecast", "climate"]
        self.api_key = "your_openweathermap_api_key"  # Replace with your API key
    
    def handle_command(self, command: str, **kwargs) -> str:
        """Handle weather-related commands"""
        city = self.extract_city(command)
        
        if any(word in command.lower() for word in ["forecast", "prediction", "tomorrow"]):
            return self.get_forecast(city)
        else:
            return self.get_current_weather(city)
    
    def extract_city(self, text: str) -> str:
        """Extract city name from command text"""
        text = text.lower()
        
        # Look for patterns like "weather in Paris" or "temperature for London"
        patterns = [
            r"(?:in|for|at)\s+([a-zA-Z\s]+?)(?:\s|$)",
            r"weather\s+([a-zA-Z\s]+?)(?:\s|$)",
            r"temperature\s+([a-zA-Z\s]+?)(?:\s|$)"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                city = match.group(1).strip()
                if city and len(city) > 1:
                    return city.title()
        
        return "London"  # Default city
    
    def get_current_weather(self, city: str) -> str:
        """Get current weather for a city"""
        if self.api_key == "your_openweathermap_api_key":
            return f"Weather plugin needs API key configuration. Would show weather for {city}."
        
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={self.api_key}&units=metric"
        
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            weather = data["weather"][0]["description"].title()
            temp = data["main"]["temp"]
            feels_like = data["main"]["feels_like"]
            humidity = data["main"]["humidity"]
            
            return (f"Current weather in {city}:\n"
                   f"🌡️ Temperature: {temp}°C (feels like {feels_like}°C)\n"
                   f"🌤️ Condition: {weather}\n"
                   f"💧 Humidity: {humidity}%")
                   
        except requests.exceptions.RequestException as e:
            return f"Error fetching weather data for {city}: {e}"
        except KeyError as e:
            return f"Invalid response format for {city}. City might not exist."
        except Exception as e:
            return f"Unexpected error getting weather for {city}: {e}"
    
    def get_forecast(self, city: str) -> str:
        """Get weather forecast for a city"""
        if self.api_key == "your_openweathermap_api_key":
            return f"Weather forecast plugin needs API key configuration. Would show forecast for {city}."
        
        url = f"http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={self.api_key}&units=metric"
        
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            forecast_text = f"5-day forecast for {city}:\n"
            
            # Get forecast for next 5 days (every 24 hours)
            for i in range(0, min(len(data["list"]), 5), 8):  # Every 8th entry is ~24 hours
                forecast = data["list"][i]
                date = forecast["dt_txt"].split()[0]
                weather = forecast["weather"][0]["description"].title()
                temp = forecast["main"]["temp"]
                
                forecast_text += f"📅 {date}: {weather}, {temp}°C\n"
            
            return forecast_text
            
        except Exception as e:
            return f"Error fetching forecast for {city}: {e}"

# Legacy support - keep these functions for backward compatibility
def get_weather(city):
    plugin = WeatherPlugin()
    return plugin.get_current_weather(city)

def handle_command(text):
    plugin = WeatherPlugin()
    return plugin.handle_command(text)
