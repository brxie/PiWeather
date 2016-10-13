#!/usr/bin/env python
from lib.forecast import DarkskyWeather
from lib.view import LCDView
from time import sleep
import threading


apikey = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
weather = DarkskyWeather(apikey, 71.0281183, -8.1249335, units = 'auto', lang = 'en')

CONDITION_REFRESH_INTERVAL = 30
FORECAST_REFRESH_INTERVAL = 600


def condition(lcd, mutex):
    lastCond = None
    while True:
        cond = weather.condition
        if cond != lastCond:
            mutex.acquire()
            lcd.condition(cond)
            lastCond = cond
            mutex.release()
        sleep(CONDITION_REFRESH_INTERVAL)

def forecast(lcd, mutex):
    lastFcst = None
    while True:
        fcst = weather.forecast
        if fcst != lastFcst:
            mutex.acquire()
            lcd.forecast(fcst)
            lastFcst = fcst
            mutex.release()
        sleep(FORECAST_REFRESH_INTERVAL)


lcd = LCDView()
lcd.initScreen()

threads = []
mutex = threading.Lock()
threads.append(threading.Thread(target = condition, args = [lcd, mutex]))
threads.append(threading.Thread(target = forecast, args = [lcd, mutex]))

for thrd in threads:
    thrd.start()
