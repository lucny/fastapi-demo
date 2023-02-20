# https://realpython.com/beautiful-soup-web-scraper-python/
# Modul requests (pip install requests)
import requests
# Import knihovny BeautifulSoup4 (pip install beautifulsoup4), která usnadňuje web scraping
from bs4 import BeautifulSoup
import json

# Konstanta obsahující adresu webu, z něhož chceme získávat data
# Žebříček 250 nejlépe hodnocených filmů podle serveru imdb.com
URL = 'https://www.imdb.com/chart/top'
# URL = 'https://www.csfd.cz/zebricky/filmy/nejlepsi/'

# Odeslání požadavku metodou get na určenou URL adresu - HTTP server vrací zpět obsah stránky
# page = requests.get(URL, headers={'User-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36'})
page = requests.get(URL)
# Vytvoření objektu parseru stránky
soup = BeautifulSoup(page.content, 'html.parser')
movie_links = soup.select('td.titleColumn>a')
# movie_links = soup.select('article .film-title-norating')
year_links = soup.select('td.titleColumn>span')
rating_links = soup.select('td.ratingColumn>strong')
# Získání názvů filmů
titles = [tag.text for tag in movie_links]
# Získání roků vzniku filmů
years = [int(tag.text[1:-1]) for tag in year_links]
# Získání hodnocení
ratings = [float(tag.text) for tag in rating_links]
# Získání režisérů
directors = [tag['title'].split(',')[0][:-7] for tag in movie_links]
# Získání herců
actors = [tag['title'].split(', ')[1:] for tag in movie_links]
# Odkazy na detaily filmů
urls = [f'https://www.imdb.com{tag["href"]}' for tag in movie_links]
# Kontrolní výpis získaných údajů

with open("movies.json",  "w", encoding='utf-8') as file:
    file.write('[')
    for i in range(0, 250):
        detail_page = requests.get(urls[i], headers={'User-agent': 'Mozilla/5.0'})
        dsoup = BeautifulSoup(detail_page.content, 'html.parser')
        content = dsoup.select('[data-testid=plot]>span[data-testid=plot-xs_to_m]')
        runtime = (dsoup.select('[data-testid=hero-title-block__metadata]>li:last-child'))[0].text[0:-1].split('h ')
        genre_links = dsoup.select('[data-testid=genres] a')
        genres = [genre.text for genre in genre_links]
        print(genres)
        if len(runtime) > 1:
            runtime = int(runtime[0]) * 60 + int(runtime[1])
        else:
            runtime = int(runtime[0]) * 60
        row = f'"title": "{titles[i]}", "year": {years[i]}, "runtime": {runtime}, "rating": {ratings[i]}, "description": "{content[0].text}", "director": "{directors[i]}", "actors": {json.dumps(actors[i])}, "url": "{urls[i]}", "genres": {json.dumps(genres)}'
        row = '{' + row + '}, '
        print(row)
        file.write(row)
    file.write(']')