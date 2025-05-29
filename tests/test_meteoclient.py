#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime, timezone
import unittest
import os
import responses
from swissweather.meteo import MeteoClient

TEST_PATH = os.path.dirname(os.path.realpath(__file__))

class TestMeteoClient(unittest.TestCase):

    @responses.activate
    def test_forecast_full_response(self):
        responses.add(**{
            'method'         : responses.GET,
            'url'            : 'https://app-prod-ws.meteoswiss-app.ch/v1/plzDetail?plz=999900',
            'body'           : open(os.path.join(TEST_PATH, "full_forecast_response.json"), "rb"),
            'status'         : 200,
            'content_type'   : 'application/json',
        })

        client = MeteoClient()    
        forecast = client.get_forecast(9999)
        self.assertIsNotNone(forecast)

    @responses.activate
    def test_forecast_broken_response(self):
        responses.add(**{
            'method'         : responses.GET,
            'url'            : 'https://app-prod-ws.meteoswiss-app.ch/v1/plzDetail?plz=999900',
            'body'           : "ay caramba",
            'status'         : 200,
            'content_type'   : 'application/json',
        })

        client = MeteoClient()    
        forecast = client.get_forecast(9999)
        self.assertIsNone(forecast)

    @responses.activate
    def test_forecast_error_response(self):
        responses.add(**{
            'method'         : responses.GET,
            'url'            : 'https://app-prod-ws.meteoswiss-app.ch/v1/plzDetail?plz=999900',
            'body'           : "",
            'status'         : 403,
            'content_type'   : 'application/json',
        })

        client = MeteoClient()    
        forecast = client.get_forecast(9999)
        self.assertIsNone(forecast)

    @responses.activate
    def test_current_weather_full_response_one_station(self):
        responses.add(**{
            'method'         : responses.GET,
            'url'            : 'https://data.geo.admin.ch/ch.meteoschweiz.messwerte-aktuell/VQHA80.csv',
            'body'           : open(os.path.join(TEST_PATH, "full_current_response.csv"), "rb"),
            'status'         : 200,
            'content_type'   : 'binary/octet-stream',
        })

        client = MeteoClient()    
        status = client.get_current_weather_for_station("KLO")        
        self.assertIsNotNone(status)
        self.assertEqual(status.airTemperature, (24.8, "°C"))
        self.assertEqual(status.precipitation, (1.32, "mm"))
        self.assertEqual(status.sunshine, (10, "min"))

    @responses.activate
    def test_pollen_stations_response(self):
        responses.add(**{
            'method'         : responses.GET,
            'url'            : 'https://data.geo.admin.ch/ch.meteoschweiz.ogd-pollen/ogd-pollen_meta_stations.csv',
            'body'           : open(os.path.join(TEST_PATH, "pollen_stations_response.csv"), "rb"),
            'status'         : 200,
            'content_type'   : 'binary/octet-stream',
        })

        client = MeteoClient()
        status = client.get_pollen_station_list()
        self.assertIsNotNone(status)
        self.assertEqual(len(status), 16)

        last_station = status[-1]
        print(last_station)
        self.assertEqual(last_station.abbreviation, 'PZH')
        self.assertEqual(last_station.name, 'Zürich') # Umlaut needs to be correctly converted to UTF
        self.assertEqual(last_station.type, 'Pollen stations')
        self.assertEqual(last_station.altitude, 559.0)
        self.assertEqual(last_station.lat, 47.378225)
        self.assertEqual(last_station.lng, 8.565644)
        self.assertEqual(last_station.canton, 'ZH')

    @responses.activate
    def test_pollen_stations_error_response(self):
        responses.add(**{
            'method'         : responses.GET,
            'url'            : 'https://data.geo.admin.ch/ch.meteoschweiz.ogd-pollen/ogd-pollen_meta_stations.csv',
            'body'           : None,
            'status'         : 404,
            'content_type'   : 'binary/octet-stream',
        })

        client = MeteoClient()
        stations = client.get_pollen_station_list()
        self.assertIsNone(stations)

    @responses.activate
    def test_pollen_current_state_response(self):
        responses.add(**{
            'method'         : responses.GET,
            'url'            : 'https://data.geo.admin.ch/ch.meteoschweiz.ogd-pollen/pbe/ogd-pollen_pbe_d_recent.csv',
            'body'           : open(os.path.join(TEST_PATH, "pollen_data_response.csv"), "rb"),
            'status'         : 200,
            'content_type'   : 'binary/octet-stream',
        })

        client = MeteoClient()
        status = client.get_current_pollen_for_station('PBE')
        self.assertIsNotNone(status)

        print(status)

        self.assertEqual(status.stationAbbr, 'PBE')
        self.assertEqual(status.timestamp, datetime(2025, 5, 28, 23, 0, tzinfo=timezone.utc))
        self.assertEqual(status.birch[0], 43)
        self.assertEqual(status.grasses[0], 6)
        self.assertEqual(status.alder[0], 33)
        self.assertEqual(status.hazel[0], 21)
        self.assertEqual(status.beech[0], 4)
        self.assertEqual(status.ash[0], 5)
        self.assertEqual(status.oak[0], 4)


    @responses.activate
    def test_pollen_current_state_error_response(self):
        responses.add(**{
            'method'         : responses.GET,
            'url'            : 'https://data.geo.admin.ch/ch.meteoschweiz.ogd-pollen/ogd-pollen_meta_stations.csv',
            'body'           : None,
            'status'         : 404,
            'content_type'   : 'binary/octet-stream',
        })

        client = MeteoClient()
        status = client.get_current_pollen_for_station('PBE')
        self.assertIsNone(status)

if __name__ == "__main__":
    unittest.main()