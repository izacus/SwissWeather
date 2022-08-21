import csv
from dataclasses import dataclass
import functools
import requests
import logging
import json
from datetime import datetime, timezone
from typing import NewType


logger = logging.getLogger(__name__)

STATION_URL = "https://data.geo.admin.ch/ch.meteoschweiz.messnetz-automatisch/ch.meteoschweiz.messnetz-automatisch_en.csv"
CURRENT_CONDITION_URL= 'https://data.geo.admin.ch/ch.meteoschweiz.messwerte-aktuell/VQHA80.csv'

FORECAST_URL= "https://app-prod-ws.meteoswiss-app.ch/v1/plzDetail?plz={}00"
FORECAST_USER_AGENT = "android-31 ch.admin.meteoswiss-2160000"

CONDITION_CLASSES = {
    "clear-night": [101],
    "cloudy": [5,35,105,135],
    "fog": [27,28,127,128],
    "hail": [],
    "lightning": [12,112],
    "lightning-rainy": [13,23,24,25,32,113,123,124,125,132],
    "partlycloudy": [2,3,4,102,103,104],
    "pouring": [20,120],
    "rainy": [6,9,14,17,29,33,106,109,114,117,129,133],
    "snowy": [8,11,16,19,22,30,34,108,111,116,119,122,130,134],
    "snowy-rainy": [7,10,15,18,21,31,107,110,115,118,121,131],
    "sunny": [1,26,126],
    "windy": [],
    "windy-variant": [],
    "exceptional": [],
}

ICON_TO_CONDITION_MAP =  {i: k for k, v in CONDITION_CLASSES.items() for i in v}

"""
Returns float or None
"""
def to_float(string: str) -> float:
    if string is None:
        return None

    try:
        return float(string)
    except ValueError:
        return None

def to_int(string: str) -> float:
    if string is None:
        return None

    try:
        return int(string)
    except ValueError:
        return None

FloatValue = NewType('FloatValue', tuple[float, str])

@dataclass
class StationInfo(object):
    name: str
    abbreviation: str
    type: str
    altitude: float
    lat: float
    lng: float
    canton: str

    def __str__(self) -> str:
        return f"Station {self.abbreviation} - [Name: {self.name}, Lat: {self.lat}, Lng: {self.lng}, Canton: {self.canton}]"

    def __hash__(self) -> int:
        return hash(self.name, self.abbreviation)

@dataclass
class CurrentWeather(object):
    station: StationInfo
    date: datetime
    airTemperature: FloatValue
    precipitation: FloatValue
    sunshine: FloatValue
    globalRadiation: FloatValue
    relativeHumidity: FloatValue
    dewPoint: FloatValue
    windDirection: FloatValue
    windSpeed: FloatValue
    gustPeak1s: FloatValue
    pressureStationLevel: FloatValue
    pressureSeaLevel: FloatValue
    pressureSeaLevelAtStandardAtmosphere: FloatValue

@dataclass
class CurrentState(object):
    currentTemperature: FloatValue
    currentIcon: int
    currentCondition: str    

@dataclass
class Forecast(object):
    timestamp: datetime
    icon: int
    condition: str
    temperatureMax: FloatValue
    temperatureMin: FloatValue
    precipitation: FloatValue

@dataclass
class WeatherForecast(object):
    current: CurrentState
    dailyForecast: list[Forecast]

class MeteoClient(object):
    def __init__(self):
        logger.debug("Initializing client.")

    def get_current_weather_for_all_stations(self) -> list[CurrentWeather]:
        logger.debug("Retrieving current weather for all stations ...")
        data = self._get_csv_dictionary_for_url(CURRENT_CONDITION_URL)
        weather = []
        for row in data:
            weather.append(self._get_current_data_for_row(row))
        return weather

    def get_current_weather_for_station(self, station: str) -> CurrentWeather:
        logger.debug("Retrieving current weather...")
        data = self._get_current_weather_line_for_station(station)
        if data is None:
            logger.warning(f"Couldn't find data for station {station}")
            return None

        return self._get_current_data_for_row(data)

    @functools.lru_cache(maxsize=1)
    def get_all_stations(self, temperatureOnly = False) -> list[StationInfo]:
        SKIP_NAMES = ['creation_time', 'map_short_name', 'license']
        all_station_data = self._get_csv_dictionary_for_url(STATION_URL, encoding='latin1')
        stations = {}
        for row in all_station_data:            
            if row.get('Station', None) in SKIP_NAMES:
                continue
            if temperatureOnly and "Temperature" not in row.get('Measurements', ""):
                continue

            abbr = row.get('Abbr.', None)
            stations[abbr] = StationInfo(
                row.get('Station', None),
                abbr,
                row.get('Station type', None),
                to_float(row.get('Station height m a. sea level', None)),
                to_float(row.get('Latitude', None)),
                to_float(row.get('Longitude', None)),
                row.get('Canton', None)
            )      
        return stations

    def _get_current_data_for_row(self, csv_row):
        timestamp = None
        timestamp_raw = csv_row.get('Date', None)
        if timestamp_raw is not None:
            timestamp = datetime.strptime(timestamp_raw, '%Y%m%d%H%M').replace(tzinfo=timezone.utc)
        
        station_data = CurrentWeather(
            self.get_all_stations().get(csv_row.get('Station/Location')),
            timestamp,
            (to_float(csv_row.get('tre200s0', None)), "°C") ,
            (to_float(csv_row.get('rre150z0', None)), "mm"),
            (to_float(csv_row.get('sre000z0', None)), "min"),
            (to_float(csv_row.get('gre000z0', None)), "W/m²"),
            (to_float(csv_row.get('ure200s0', None)), '%'),
            (to_float(csv_row.get('tde200s0', None)), '°C'),
            (to_float(csv_row.get('dkl010z0', None)), '°'),
            (to_float(csv_row.get('fu3010z0', None)), 'km/h'),
            (to_float(csv_row.get('fu3010z1', None)), 'km/h'),
            (to_float(csv_row.get('prestas0', None)), 'hPa'),
            (to_float(csv_row.get('prestas0', None)), 'hPa'),
            (to_float(csv_row.get('pp0qnhs0', None)), 'hPa'),
        )

        return station_data

    def _get_current_weather_line_for_station(self, station):        
        return next((row for row in self._get_csv_dictionary_for_url(CURRENT_CONDITION_URL)
            if row['Station/Location'] == station), None)
         
    def _get_csv_dictionary_for_url(self, url, encoding='utf-8'):
        try:
            with requests.get(url, stream = True) as r:
                lines = (line.decode(encoding) for line in r.iter_lines())
                for row in csv.DictReader(lines, delimiter=';'):
                    yield row
        except requests.exceptions.RequestException as e:
            logger.error("Connection failure.", exc_info=1)
            return None            

    ## Forecast
    def get_forecast(self, postCode, language="en") -> WeatherForecast:
        forecastJson = self._get_forecast_json(postCode, langugage=language)
        currentState = self._get_current_state(forecastJson)
        dailyForecast = self._get_daily_forecast(forecastJson)
        return WeatherForecast(currentState, dailyForecast)    

    def _get_current_state(self, forecastJson) -> CurrentState:
        if "currentWeather" not in forecastJson:
            return None

        currentIcon = to_int(forecastJson.get('currentWeather', {}).get('icon', None))
        currentCondition = None
        if currentIcon is not None:
            currentCondition = ICON_TO_CONDITION_MAP.get(currentIcon, None)
        return CurrentState(
            (to_float(forecastJson.get('currentWeather', {}).get('temperature')), "°C"),
            currentIcon, currentCondition)        
        
    def _get_daily_forecast(self, forecastJson) -> list[Forecast]:
        forecast = []
        if "forecast" not in forecastJson:
            return forecast

        for dailyJson in forecastJson["forecast"]:
            timestamp = None
            if "dayDate" in dailyJson:
                timestamp = datetime.strptime(dailyJson["dayDate"], '%Y-%m-%d')
            icon = to_int(dailyJson.get('iconDay', None))
            condition = ICON_TO_CONDITION_MAP.get(icon, None)
            temperatureMax = (to_float(dailyJson.get('temperatureMax', None)), "°C")
            temperatureMin = (to_float(dailyJson.get('temperatureMin', None)), "°C")
            precipitation = (to_float(dailyJson.get('precipitation', None)), "mm")
            forecast.append(Forecast(timestamp, icon, condition, temperatureMax, temperatureMin, precipitation))
        return forecast

    def _get_forecast_json(self, postCode, langugage="en"):
        try:
            url = FORECAST_URL.format(postCode)
            return requests.get(url, headers = 
                { "User-Agent": FORECAST_USER_AGENT, 
                  "Accept-Language": langugage, 
                  "Accept": "application/json" }).json()
        except requests.exceptions.RequestException as e:
            logger.error("Connection failure.", exc_info=1)
            return None            
