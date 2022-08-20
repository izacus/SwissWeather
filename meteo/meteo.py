import csv
from dataclasses import dataclass
import functools
import requests
import logging
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

MS_BASE_URL = 'https://www.meteosuisse.admin.ch'
STATION_URL = "https://data.geo.admin.ch/ch.meteoschweiz.messnetz-automatisch/ch.meteoschweiz.messnetz-automatisch_en.csv"
CURRENT_CONDITION_URL= 'https://data.geo.admin.ch/ch.meteoschweiz.messwerte-aktuell/VQHA80.csv'

JSON_FORECAST_URL = 'https://app-prod-ws.meteoswiss-app.ch/v1/forecast?plz={}00&graph=false&warning=true'
MS_SEARCH_URL = 'https://www.meteosuisse.admin.ch/home/actualite/infos.html?ort={}&pageIndex=0&tab=search_tab'


MS_24FORECAST_URL = "https://www.meteosuisse.admin.ch/product/output/forecast-chart/{}/fr/{}00.json"
MS_24FORECAST_REF = "https://www.meteosuisse.admin.ch//content/meteoswiss/fr/home.mobile.meteo-products--overview.html"

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

class MeteoClient(object):
    def __init__(self):
        logger.debug("Initializing client.")

    def get_current_weather_for_all_stations(self):
        logger.debug("Retrieving current weather for all stations ...")
        data = self._get_csv_dictionary_for_url(CURRENT_CONDITION_URL)
        weather = []
        for row in data:
            weather.append(self._get_current_data_for_row(row))
        return weather

    def get_current_weather_for_station(self, station: str):
        logger.debug("Retrieving current weather...")
        data = self._get_current_weather_line_for_station(station)
        if data is None:
            logger.warning(f"Couldn't find data for station {station}")
            return None

        return self._get_current_data_for_row(data)

    @functools.lru_cache(maxsize=1)
    def get_all_stations(self):
        SKIP_NAMES = ['creation_time', 'map_short_name', 'license']
        all_station_data = self._get_csv_dictionary_for_url(STATION_URL, encoding='latin1')
        stations = {}
        for row in all_station_data:            
            if row.get('Station', None) in SKIP_NAMES:
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
        
        station_data = {
            "station": csv_row.get('Station/Location'),
            "date": timestamp,
            "air_temperature": (to_float(csv_row.get('tre200s0', None)), "°C") ,
            "precipitation_10min": (to_float(csv_row.get('rre150z0', None)), "mm"),
            "sunshine_10min": (to_float(csv_row.get('sre000z0', None)), "min"),
            "global_radiation_10min": (to_float(csv_row.get('gre000z0', None)), "W/m²"),
            "relative_humidity": (to_float(csv_row.get('ure200s0', None)), '%'),
            "dew_point": (to_float(csv_row.get('tde200s0', None)), '°C'),
            "wind_direction_10min": (to_float(csv_row.get('dkl010z0', None)), '°'),
            "wind_speed_10min": (to_float(csv_row.get('fu3010z0', None)), 'km/h'),
            "gust_peak_1s": (to_float(csv_row.get('fu3010z1', None)), 'km/h'),
            "pressure_station_level": (to_float(csv_row.get('prestas0', None)), 'hPa'),
            "pressure_sea_level": (to_float(csv_row.get('prestas0', None)), 'hPa'),
            "pressure_sea_level_at_std_atmosphere": (to_float(csv_row.get('pp0qnhs0', None)), 'hPa'),
        }

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