from tokenize import Intnumber
import requests
import json
from dataclasses import dataclass
from datetime import datetime
from bs4 import BeautifulSoup

JSON_FORECAST_URL = 'https://app-prod-ws.meteoswiss-app.ch/v1/forecast?plz={}00&graph=false&warning=true'
MS_24FORECAST_URL = "https://www.meteosuisse.admin.ch/product/output/forecast-chart/{}/de/{}00.json"
MS_24FORECAST_REF = "https://www.meteosuisse.admin.ch//content/meteoswiss/fr/home.mobile.meteo-products--overview.html"

MS_BASE_URL = 'https://www.meteosuisse.admin.ch'
MS_SEARCH_URL = 'https://www.meteosuisse.admin.ch/home/actualite/infos.html?ort={}&pageIndex=0&tab=search_tab'

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

@dataclass
class Forecast(object):
    date: datetime
    # Icon of the weather, integer, needs to be remapped.
    icon: int
    condition: str
    temperatureMax: int
    temperatureMin: int
    precipitation: float

def get_forecast(postCode: int) -> list[Forecast]:
    s = requests.Session()
    #Forcing headers to avoid 500 error when downloading file
    s.headers.update({"Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Accept-Encoding":"gzip, deflate, sdch",'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/1337 Safari/537.36'})

    jsonUrl = JSON_FORECAST_URL.format(postCode)
    jsonData = s.get(jsonUrl,timeout=10)
    jsonDataTxt = jsonData.text
    jsonObj = json.loads(jsonDataTxt)

    # We'll get strangely empty JSON if the postCode is wrong
    # so return this as None
    if jsonObj.get('plz', 0) == 0:
        return None

    regionForecast = jsonObj.get('regionForecast', None)
    if regionForecast is None:
        return None

    forecast = []
    for day in regionForecast:
        dateString = day.get('dayDate', None)
        if dateString is None:
            continue
        dayDate = datetime.strptime(dateString, '%Y-%m-%d')
        dayForecast = Forecast(dayDate, day.get('iconDay', 0), 
                                ICON_TO_CONDITION_MAP.get(day.get('iconDay', -1), None),
                                day.get('temperatureMax', 0), 
                                day.get('temperatureMin', 0), 
                                day.get('precipitation', 0))
        forecast.append(dayForecast)
    return forecast

def get_24hr_forecast(postCode:int) -> list[Forecast]:
    s = requests.Session()
    #Forcing headers to avoid 500 error when downloading file
    s.headers.update({"Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Accept-Encoding":"gzip, deflate, sdch",'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/1337 Safari/537.36'})
    searchUrl = MS_SEARCH_URL.format(postCode)
    tmpSearch = s.get(searchUrl,timeout=10)

    print(tmpSearch)

    soup = BeautifulSoup(tmpSearch.text,features="html.parser")
    widgetHtml = soup.find_all("section",{"id": "weather-widget"})
    print(widgetHtml)

    #jsonUrl = widgetHtml[0].get("data-json-url")
    #jsonUrl = str(jsonUrl)
    #version = jsonUrl.split('/')[5]
    #forecastUrl = MS_24FORECAST_URL.format(version,postCode)
    #s.headers.update({'referer': MS_24FORECAST_REF,"x-requested-with": "XMLHttpRequest","Accept": "application/json, text/javascript, */*; q=0.01","dnt": "1"})
    #jsonData = s.get(forecastUrl,timeout=10)
    #jsonData.encoding = "utf8"
    #jsonDataTxt = jsonData.text

    #jsonObj = json.loads(jsonDataTxt)
    #print(jsonObj)

