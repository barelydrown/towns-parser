import json
import re
import datetime

import requests
from bs4 import BeautifulSoup

HOST = 'https://geogoroda.ru/'
HEADERS = {
    'user-agent': ('Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:71.0) '
                   'Gecko/20100101 Firefox/71.0'),
    'accept': '*/*'
}


def get_html(url, params=None):
    r = requests.get(url, headers=HEADERS, params=params)
    return r


def get_html_content(url, params=None):
    r = requests.get(url, headers=HEADERS, params=params)
    return r.content


def get_letters(html):
    """Возвращает список первых букв городов"""
    soup = BeautifulSoup(html, 'html.parser')
    pagination = soup.find('h4', class_='goroda-bukva').get_text(strip=True)
    letters = []
    for n in pagination:
        letters.append(n.lower())
    return letters


def get_urls(url):
    """Возвращает список ссылок на страницы со всеми городами"""
    html = get_html_content(url)
    letters = get_letters(html)
    all_urls = []
    for letter in letters:
        all_urls.append(url + letter)
    return all_urls


def get_pagination(letter):
    """Возвращает количество страниц городов, на букву в аргументе"""
    url = f'https://geogoroda.ru/bukva/{letter}'
    html = get_html_content(url)
    soup = BeautifulSoup(html, 'html.parser')

    try:
        try:
            item = soup.find('li', class_='pager-last even last').find('a')['href']
        except:
            item = soup.find('li', class_='pager-last odd last').find('a')['href']
    except:
        return 0

    pages_count = int(re.findall(r'\d+$', item)[0])
    return pages_count


def parse_all():
    """
    Парсит названия всех городов мира на всевозможные буквы,
    записывает значения в словарь, где ключом является буква,
    а значением список городов, начинающихся на эту букву.
    Записывает данный словарь в json-файл.
    """
    start_url = 'https://geogoroda.ru/bukva/а'
    html = get_html_content(start_url)
    letters = get_letters(html)

    main_dict = {}
    main_list = []
    counter = 0
    start = datetime.datetime.now().strftime('%H:%M:%S')

    for letter in letters:
        page_count = get_pagination(letter)
        towns_list = []
        for page in range(0, page_count + 1):
            url = f'https://geogoroda.ru/bukva/{letter}?page={page}'
            html = get_html_content(url)
            soup = BeautifulSoup(html, 'html.parser')
            items = soup.find_all('td', class_='views-field views-field-title large')
            for item in items:
                town = item.find('a').get_text()
                main_list.append(town)
                towns_list.append(town)
                print(f'Добавлен город №{counter}')
                counter += 1

        main_dict[letter.title()] = towns_list

        with open('data/towns_dict.json', 'w') as file1:
            json.dump(main_dict, file1, ensure_ascii=False, indent=4)
        with open('data/towns_list.json', 'w') as file2:
            json.dump(main_list, file2, ensure_ascii=False, indent=4)

        print(f'Добавлены все города на букву: {letter.upper()}')
    print(f'Всего городов: {counter}')

    end = datetime.datetime.now().strftime('%H:%M:%S')
    print(f'Время начала: {start}')
    print(f'Время окончания: {end}')


def parse_ru(url):
    """
    Парсит названия всех городов России на всевозможные буквы,
    записывает значения в словарь, где ключом является буква,
    а значением список городов, начинающихся на эту букву.
    Записывает данный словарь в json-файл.
    """
    URLS = get_urls(url)
    main_dict = {}
    letter_list = []

    for url in URLS:
        html = get_html_content(url)
        soup = BeautifulSoup(html, 'html.parser')
        items = soup.find_all('td', class_='views-field views-field-title large')
        letter = url[-1].upper()

        for item in items:
            letter_list.append(item.find('a').get_text())

            main_dict[letter] = letter_list

        letter_list = []

    with open('data/ru/ru_towns_dict.json', 'w', encoding='utf-8') as file:
        json.dump(main_dict, file, ensure_ascii=False, indent=4)


def get_town_url(html):
    """Возвращает ссылку на страницу города в Википедии"""
    soup = BeautifulSoup(html, 'html.parser')
    wiki_url = soup.find('div', class_='yuRUbf').find('a')['href']
    return wiki_url
