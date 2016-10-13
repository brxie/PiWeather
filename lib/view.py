from os import path
from pylcd import ks0108
from collections import defaultdict


class Icons(object):
    ICONS = {
        "clear-day": {
            "file": "media/001.png",
            "intensity": None
        },
        "clear-night": {
            "file": "media/006.png",
            "intensity": None
        },
        "rain": {
            "file": [
                "media/012.png",
                "media/013.png",
                "media/014.png"
            ],
            "intensity": {
                "type": "precipIntensity",
                "levels": [
                    0.5,
                    1.5,
                    5,
                ]
            }
        },
        "snow": {
            "file": [
                "media/020.png",
                "media/021.png",
                "media/022.png"
            ],
            "intensity": {
                "type": "precipIntensity",
                "levels": [
                    0.5,
                    1.5,
                    5,
                ]
            }
        },
        "sleet": {
            "file": "media/023.png"
        },
        "wind": {
            "file": "media/031.png",
            "intensity": None
        },
        "fog": {
            "file": "media/030.png",
            "intensity": None
        },
        "cloudy": {
            "file": "media/011.png",
            "intensity": None
        },
        "partly-cloudy-day": {
            "file": [
                "media/003.png",
                "media/002.png",
                "media/004.png"
            ],
            "intensity": {
                "type": "cloudCover",
                "levels": [
                    0.5,
                    0.8,
                    1.0
                ]
            }
        },
        "partly-cloudy-night": {
            "file": [
                "media/008.png",
                "media/007.png",
                "media/009.png"
            ],
            "intensity": {
                "type": "cloudCover",
                "levels": [
                    0.5,
                    0.8,
                    1.0
                ]
            }
        },
        "hail": {
            "file": "media/018.png",
            "intensity": None
        },
        "thunderstorm": {
            "file": "media/016.png",
            "intensity": None
        },
        "tornado": {
            "file": "media/027.png",
            "intensity": None
        },
        "na": {
            "file": "media/000.png",
            "intensity": None
        }
    }

class LCDView(Icons):

    PINMAP = {
        'RS': 7,
        'RW': 8,
        'E': 4,
        'RST': 25,
        'D0': 14,
        'D1': 15,
        'D2': 18,
        'D3': 27,
        'D4': 22,
        'D5': 10,
        'D6': 9,
        'D7': 11,
        'LED': 17,
        'CS1': 23,
        'CS2': 24
    }

    COND_TEMP_POS = {"x": 0, "y": 45}
    FORECAST_POS = {"x": 46, "y": 0}
    LCD_BOUNDS = (128, 64)

    def __init__(self):
        dev = ks0108.Display(backend = ks0108.GPIOBackend, pinmap = self.PINMAP)
        dev.clear()
        self.lcd = ks0108.DisplayDraw(dev, auto_commit = False)
        self.fonts = [
            self._scriptDir() + '/font/tahoma.ttf',
            self._scriptDir() + '/font/tahomabd.ttf',
            self._scriptDir() + '/font/Mathmos Original.ttf'] 
        # clear screen
        self.lcd.fill_screen(self.lcd.PATTERN_EMPTY)
        self.lcd.display.commit(full = True, live = False)
        self._drawLayout()
        self._tempUnit = u'C' 

    @property
    def tempUnit(self):
        return self._tempUnit

    @tempUnit.setter
    def tempUnit(self, char):
        self._tempUnit = char

    def drawAll(self):
        pass

    def condition(self, condition):  
        temp = condition["temp"]
        self._drawCondTemp(temp)
        self._drawCondIcon(condition["icon"], condition)
        self._render()
    
    def forecast(self, forecast):
        x, y = self.FORECAST_POS['x'], self.FORECAST_POS['y']
        self._clearArea(x, y, self.LCD_BOUNDS[0], self.LCD_BOUNDS[1])

        time = forecast[0]['time']
        tempMax, tempMin = forecast[0]['high'], forecast[0]['low']
        summary =  forecast[0]['summary']

        tempStr = u'temp: {0}..{1}\u00B0C'.format(tempMin, tempMax)
        self.lcd.text(time, x, 0 , size = 11, font = self.fonts[1])
        self.lcd.text(tempStr, x, 10 , size = 9, font = self.fonts[1])

        # summary text
        maxLineChars = 16
        lines = defaultdict(str)
        lineNr = 0
        for word in summary.split():
            if len(''.join(lines[lineNr])) + len(word) > maxLineChars:
                lineNr += 1
                charsCount = 0
            lines[lineNr] += word + ' '

        rowHeight = 8
        for i, line in enumerate(lines.values()):
            self.lcd.text(line, x, (i * rowHeight) + 22, size = 9, font = self.fonts[1])

        self._render()
    
    def initScreen(self):
        self.lcd.text("init...", 0, 0, size = 12, font = self.fonts[2])
        self._render()
        self._clearArea(0, 0, 40, 20)

    def _drawLayout(self):
        self.lcd.line(44, 0, 44, self.LCD_BOUNDS[1], clear = False)
        
    def _drawIcon(self, icon, x, y, width, height):       
        fullPath = self._scriptDir() + '/' + icon
        self.lcd.image(fullPath, x, y, width, height, angle = 0, greyscale = True, condition = 'red < 224', clear = False)

    def _drawCondTemp(self, temp, size = 18):
        x, y = self.COND_TEMP_POS['x'], self.COND_TEMP_POS['y'] 
        self._clearArea(0, y, 43, y + size)
        self.lcd.text(temp, x, y, size = size, font = self.fonts[1])

    def _drawCondIcon(self, icon, condition):
        self._clearArea(0, 0, 40, 40)
        try:
            icon = self.ICONS[icon]
        except KeyError:
            icon = self.ICONS['na']
        
        if icon['intensity'] is not None:
            intensType = icon['intensity']['type']
            intensity = condition[intensType]

            for key, level in enumerate(icon['intensity']['levels']):
                if intensity <= level:
                    icoFile = icon['file'][key]
                    break
            try:
                icoFile
            except NameError:
                # get last icon when intensity exceeds scope  
                icoFile = icon['file'][-1]
        else:
            icoFile = icon['file']

        self._drawIcon(icoFile, 0, 0, 40, 40)

    def _render(self):
        self.lcd.display.commit(full = False, live = True)

    def _scriptDir(self):
        return path.dirname(path.realpath(__file__))

    def _clearArea(self, startX, startY, stopX, stopY):
        self.lcd.rectangle(startX, startY, stopX, stopY, True, True)

