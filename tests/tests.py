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

if __name__ == "__main__":
    unittest.main()