import os
import requests
from loguru import logger
from dotenv import load_dotenv

load_dotenv()

weather_tool ={
      "type": "function",
      "function": {
        "name": "get_current_temperature",
        "description": "Get the current temperature for a specific location",
        "parameters": {
          "type": "object",
          "properties": {
            "location": {
              "type": "string",
              "description": "The city and state, e.g., San Francisco, CA"
            },
            "unit": {
              "type": "string",
              "enum": ["Celsius", "Fahrenheit"],
              "description": "The temperature unit to use. Infer this from the user's location."
            }
          },
          "required": ["location", "unit"]
        }
      }
    }


def get_current_temperature(location, unit):

    base_url = "http://api.openweathermap.org/data/2.5/weather?"

    WEATHER_API_KEY = "a43159052c728369ea7931fda709429c"

    complete_url = base_url + "appid=" + WEATHER_API_KEY + "&q=" + location

    logger.info(f"get_current_temperature:: {complete_url}")
    response = requests.get(complete_url)

    x = response.json()

    if x["cod"] != "404":
 
        # store the value of "main"
        # key in variable y
        y = x["main"]
    
        # store the value corresponding
        # to the "temp" key of y
        current_temperature = y["temp"] - 273.15      
    
        # store the value of "weather"
        # key in variable z
        z = x["weather"]
    
        # store the value corresponding 
        # to the "description" key at 
        # the 0th index of z
        weather_description = str(z[0]["description"])

        output = f"Current temperature in {location}: {current_temperature}°C and it is {weather_description}"
    else:
        output = f"Error: City {location} is not found"

    logger.info(f"get_current_temperature:: {output}")
    return output