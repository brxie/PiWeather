#!/usr/bin/env python
import requests
import socket
import json
import threading
from time import sleep, strftime, localtime


class DarkskyWeather(object):
    
    MINUTE = 60

    def __init__(self, APIKey, latitude, longitude, **kwargs):
        self.lat, self.lng = latitude, longitude
        self._APIKey = APIKey
        self._kwargs = kwargs
        self._APIURL = 'https://api.darksky.net'
        self._APIParams = [key + '=' + val for key, val in kwargs.items()]
        self._refreshInterval = self.MINUTE * 2
        self._weatherData = None
        threading.Thread(target = self._asyncWorker).start()
    
    @property
    def condition(self):
        if self._weatherData is not None:
            weatherNow = self._weatherData["currently"]
            time = self._epochToLocal(weatherNow["time"])
            temp = "%0.1f" % weatherNow["temperature"]
            icon = weatherNow["icon"]
            summary = weatherNow["summary"]
            cloudCover = weatherNow["cloudCover"]
            precipIntensity = weatherNow["precipIntensity"]
        else:
            temp = '--'
            icon = None
            summary = 'n/a'
            cloudCover = None
            precipIntensity = None

        cond = {"temp": temp,
                "icon": icon,
                "summary": summary,
                "cloudCover": cloudCover,
                "precipIntensity": precipIntensity}

        return cond

    @property
    def forecast(self):
        forecast = []
        try:
            for day in self._weatherData["daily"]["data"]:
                forecast.append({
                    "time": self._epochToLocal(day['time'], '%a %d.%m'),
                    "high": "%d" % day['temperatureMax'],
                    "low": "%d" % day['temperatureMin'],
                    "summary": day['summary'],
                    "icon": day['icon']
                })
        except TypeError:
            for _ in range(7):
                forecast.append({
                    "time": "n/a",
                    "high": "--",
                    "low": "--",
                    "summary":"n/a",
                    "icon": None
                })
        return forecast      
        
    def _epochToLocal(self, timestamp, format = '%Y-%m-%d %H:%M'):
        return strftime(format, localtime(timestamp))

    def _asyncWorker(self):
        while True:
            ok = self._refreshWeather()
            if ok:
                sleep(self._refreshInterval)
            else:
                sleep(self.MIN_SECS * 5)

    def _refreshWeather(self):
        try:
            condUrl = '%s/forecast/%s/%s,%s?exclude=hourly,flags' % (self._APIURL, self._APIKey, self.lat, self.lng)
            condUrl = self._addParams(condUrl)
            resp = requests.get(condUrl)
        except Exception as err:
            print("Can not read weather data. %s" % err)
            self._weatherData = None
            return None
        
        try:
            self._weatherData = json.loads(resp.text)
        except ValueError as err:
            print("Can not parse weather data. %s, %s", (err + resp))
            self._weatherData = None
        else:
            return True

    def _addParams(self, url):
        for param in self._APIParams:
            url += '&%s' % param
        return url
