import requests
from bs4 import BeautifulSoup
import re

#Возвращает steamid для парсинга библиотеки игр
def get_profile_id(url):
    userpage = requests.get(url)
    user_page = BeautifulSoup(userpage.content, 'lxml')
    steamid = user_page.find('div', class_="commentthread_area")['id']
    steamid = ''.join([symbol for symbol in steamid if symbol if not re.findall("(?i)([a-z]+)", symbol) and symbol not in ['_']])
    return steamid