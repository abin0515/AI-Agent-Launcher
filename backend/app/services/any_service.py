import os
import requests
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Optional, Any, Union
import logging
import json
import re
from app.core.config import settings
from openai import OpenAI
from tzlocal import get_localzone
from zoneinfo import ZoneInfo

logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class AnyService:

    def __init__(self):
        self.base_url = settings.CANVAS_API_URL
        # self.headers = {"Authorization": f"Bearer {settings.CANVAS_API_KEY}"}
        self.client = OpenAI()

    def get_weather(self, latitude, longitude):
        response = requests.get(
            f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current_weather=true"
        )
        data = response.json()
        current_weather = data["current_weather"]
        return {
            "temperature": current_weather["temperature"],
            "wind_speed": current_weather["windspeed"],
            "wind_direction": current_weather["winddirection"],
            "weather_code": current_weather["weathercode"],
            "time": current_weather["time"],
        }
