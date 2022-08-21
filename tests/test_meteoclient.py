#!/usr/bin/env python
# -*- coding: utf-8 -*-

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

if __name__ == "__main__":
    unittest.main()