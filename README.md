# SwissWeather

A Python library to access weather data from the Swiss Federal Office of Meteorology and Climatology (MeteoSwiss).

## Usage

### Weather Forecast

To get the weather forecast for a specific postal code:

```python
from swissweather.meteo import MeteoClient

client = MeteoClient()
forecast = client.get_forecast(6003) # For Lucerne

if forecast:
    print(f"Current temperature in Lucerne: {forecast.current.currentTemperature[0]}°C")
    for daily in forecast.dailyForecast:
        print(f"Forecast for {daily.timestamp.date()}: {daily.condition}, max temp: {daily.temperatureMax[0]}°C, min temp: {daily.temperatureMin[0]}°C")
```

### Current Weather

To get the current weather for a specific station:

```python
from swissweather.meteo import MeteoClient

client = MeteoClient()
weather = client.get_current_weather_for_station("KLO") # For Zurich-Kloten

if weather:
    print(f"Current weather at {weather.station}:")
    print(f"  Temperature: {weather.airTemperature[0]}°C")
    print(f"  Precipitation: {weather.precipitation[0]} mm")
    print(f"  Sunshine: {weather.sunshine[0]} min")
```

### Pollen Information

To get pollen information, you first need to get a list of pollen stations:

```python
from swissweather.meteo import MeteoClient

client = MeteoClient()
pollen_stations = client.get_pollen_station_list()

if pollen_stations:
    for station in pollen_stations:
        print(station)
```

Then, you can get the current pollen data for a specific station:

```python
from swissweather.meteo import MeteoClient

client = MeteoClient()
pollen_data = client.get_current_pollen_for_station("PBE") # For Bern

if pollen_data:
    print(f"Current pollen data for {pollen_data.stationAbbr}:")
    print(f"  Birch: {pollen_data.birch[0]} No/m3")
    print(f"  Grasses: {pollen_data.grasses[0]} No/m3")
```

## Data Source

The data is provided by the Federal Office of Meteorology and Climatology MeteoSwiss. Please attribute them as the source of the data. For more information, please visit their [website](https://www.meteoswiss.admin.ch/about-us/legal-basis/terms-and-conditions-for-the-use-of-the-meteoswiss-app-and-the-meteoswiss-website.html).
