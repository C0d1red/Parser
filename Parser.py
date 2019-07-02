import requests
from mpl_toolkits.basemap import Basemap
from bs4 import BeautifulSoup as bs
import matplotlib.pyplot as plt
from tkinter import *


# For normal work
HEADERS = {'accept': '*/*',
           'user-agent': 'Mozilla/5.0 (Windows NT 10.0; '
            'Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
            'Chrome/72.0.3626.121 Safari/537.36'
          }

# DefaultUrls
startUrl = 'https://www.cbr.ru/currency_base/dynamics/?UniDbQuery.Posted=True&UniDbQuery.mode=1' \
            '&UniDbQuery.date_req1=&UniDbQuery.date_req2=&UniDbQuery.VAL_NM_RQ=R01035&UniDbQuery.' \
            'FromDate=07.03.2019&UniDbQuery.ToDate=14.03.2019'
startUrlWeather = 'https://yandex.ru/pogoda/moscow/month'

# Parts of URL curency
MAIN_URL = 'https://www.cbr.ru/currency_base/dynamics/?UniDbQuery.Posted=True&UniDbQuery.mode=1' \
            '&UniDbQuery.date_req1=&UniDbQuery.date_req2=&UniDbQuery.VAL_NM_RQ=R01035&UniDbQuery.' \
            'FromDate='
fromDateUrl = '10.01.2019'
BETWEEN_DATE_URL = '&UniDbQuery.ToDate='
endDateUrl = '14.03.2019'

# Weather
MAIN_URL_WEATHER = 'https://yandex.ru/pogoda/'
cityDefUrl = 'moscow'
endWeatherUrl = '/month'

# Aircrafts
API_KEY = '2ff947-655ab9'
# Searching by flight iataNumber. Part of url in radarbox24
AIR_GET_URL = 'http://aviation-edge.com/v2/public/flights?key=2ff947-655ab9&flightIata=EK9707'
MAIN_URL_AIRCTAFT = 'http://aviation-edge.com/v2/public/flights?key=2ff947-655ab9&flightIata='
defAirNum = 'MU2685'

def ChoosePeriod(fromDate, endDate):
    startUrl = MAIN_URL + fromDate + BETWEEN_DATE_URL + endDate
    ParseCurency(startUrl) # Start parsing

def ChooseCity(name):
    if(name == ''):
        name = cityDefUrl
    startUrlWeather = MAIN_URL_WEATHER + name + endWeatherUrl
    ParseWeather(startUrlWeather) # Start parsing

def ChooseAircraft(airNum):
    startAirUrl = MAIN_URL_AIRCTAFT + airNum
    GetAircraft(startAirUrl)


def GetAircraft(startAircraftUrl):
    session = requests.Session()
    request = session.get(startAircraftUrl, headers=HEADERS)  # Request from server
    if request.status_code == 200:
        print('OK')
        print(request.json())
        lattitude = request.json()[0]['geography']['latitude'] #lat from request
        longitude = request.json()[0]['geography']['longitude'] #lon from request
        print(request.json()[0]['geography']['latitude'])
        print(request.json()[0]['geography']['longitude'])
        ShowAirGraph(lattitude, longitude)  # Show graph
    else:
        print('ERROR')

def ParseWeather(startWeatherUrl):
    session = requests.Session()
    request = session.get(startWeatherUrl, headers=HEADERS)  # Request from server
    if request.status_code == 200:
        print('OK')
        monthChar = '' #For dates in new Month
        soup = bs(request.content, 'html.parser')
        divs = soup.find_all('div', attrs = {'class': 'climate-calendar-day'})
        dateArr = []
        valueArr = [] #temperature

        for c in  divs:
            value = c.find('span', attrs = {'class': 'temp__value'}).text
            date = c.find('div', attrs = {'class': 'climate-calendar-day__day'}).text

            # Replace Yandex symbol to standsrt '-'
            if('−' in value):
                value = value.replace('−', '-')

            #Temperature to int for sort into graph
            value = int(value)

            # New month
            if (' ' in date):
                monthChar = date[2]

            # If new month
            if(monthChar != ''):
                date = date + ' ' + monthChar #Put new char after ' '

            dateArr.append(date)
            valueArr.append(value)

        print('Date: ' + str(dateArr))
        print('Value: ' + str(valueArr))
        ShowGraph(dateArr, valueArr, currency=False)  # Show graph

    else:
        print('ERROR')

def ParseCurency(startUrl):
    session = requests.Session()
    request = session.get(startUrl, headers=HEADERS)  # Request from server
    if request.status_code == 200:
        print('OK')
        soup = bs(request.content, 'html.parser')
        tr = soup.find_all('tr')
        dateArr = []
        valueArr = []

        for i in range(2, len(tr)):  # Start 2 because have some garbage before
            tds = tr[i].find_all('td')
            date = tds[0].text
            value = float(tds[2].text.replace(',', '.'))
            print('Date: ' + str(date) + ' Value: ' + str(value))
            dateArr.append(date)  # Add value to array
            valueArr.append(value)  # Add value to array

        ShowGraph(dateArr, valueArr, currency=True)  # Show graph
    else:
        print('ERROR')


def ShowAirGraph(lat, lon):
    m =  Basemap(projection = 'mill', llcrnrlat = -60, urcrnrlat = 90, llcrnrlon = -180, urcrnrlon = 180, resolution = 'c')
    m.drawcoastlines()
    m.fillcontinents()
    m.drawmapboundary()

    x, y = m(lon, lat)
    m.plot(x, y, 'r.')

    plt.title('Точка самолёта')
    plt.show()

def ShowGraph(date, value, currency):
    plt.plot(date, value)

    plt.plot(date, value, c = 'b') #Standart graph
    if(currency):
        print('Currency graph')
        plt.title('Фунт/рубль')
        plt.plot(date,CreateAvrGraph(value), c = 'y') #Avr graph
    else:
        plt.title('Погода')
    plt.show()

def CreateAvrGraph(value):
    valueAvr = []
    valueAvr.append(value[0])
    for i in range(1, len(value)):
        sumAvr = 0

        for j in range (0, i+1):
            sumAvr += value[j]

        sumAvr /= i+1
        valueAvr.append(sumAvr)

    return valueAvr

# GUI
gui = Tk()
gui.title('Графики')
gui.geometry('400x300')

#Start gui for currency
theLabelFrom = Label(gui, text = 'С даты (10.01.2019):')
theLabelFrom.grid(row = 0)

mEntryDateFrom = Entry(gui)
mEntryDateFrom.grid(row = 0, column = 1)


theLabelEnd = Label(gui, text = 'По дату (14.01.2019):')
theLabelEnd.grid(row = 1)

mEntryDateEnd = Entry(gui)
mEntryDateEnd.grid(row = 1, column = 1)


buttonResult = Button(gui, text = 'Валюта', command = lambda: ChoosePeriod(mEntryDateFrom.get(), mEntryDateEnd.get()))
buttonResult.grid(row = 2, column = 1)
#End gui for currency

#Start gui for weather
theLabelEnd = Label(gui, text = 'Город для погоды (moscow):')
theLabelEnd.grid(row = 4)

mEntryCity = Entry(gui)
mEntryCity.grid(row = 4, column = 1)

buttonResultWeather = Button(gui, text = 'Погода', command = lambda: ChooseCity(mEntryCity.get()))
buttonResultWeather.grid(row = 5, column = 1)
#End gui for weather

#Start gui for aircraft
theLabelAircraft = Label(gui, text = 'Номер рейса (MU2685):')
theLabelAircraft.grid(row = 6)

mEntryAircraft = Entry(gui)
mEntryAircraft.grid(row = 6, column = 1)

buttonResultAircraft = Button(gui, text = 'Точка самолёта', command = lambda: ChooseAircraft(mEntryAircraft.get()))
buttonResultAircraft.grid(row = 7, column = 1)
#End gui for aircraft

gui.mainloop()