import requests
import datetime
from bs4 import BeautifulSoup

today_date = datetime.date.today()

url = 'https://www.championat.com/stat/#' + str(today_date)
response = requests.get(url, headers={
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36"
})
bs = str(BeautifulSoup(response.text, 'lxml'))
if 'Реал' in bs:
    print('Real is playing today')
