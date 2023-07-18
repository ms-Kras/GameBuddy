import requests
from bs4 import BeautifulSoup
import re

#Возвращает steamid для парсинга библиотеки игр
def get_profile_id(url):
    userpage = requests.get(url)
    user_page = BeautifulSoup(userpage.content, 'lxml')
    text = str(user_page.find('div', class_="responsive_page_template_content"))
    steamid = int(text[text.find('"steamid"')+11:text.find('"steamid"')+28])
    return steamid