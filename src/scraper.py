import requests
import re
import csv
from bs4 import BeautifulSoup


class WebScraper:

    def __init__(self):
        self.url = "http://sindicat.net/borsa/"

    def __download(self, url):
        print("Downloading", url, "...")
        r = requests.get(url)

        return r.text

    def __get_links(self, html):
        bs = BeautifulSoup(html, "html.parser")
        nodes_a = bs.find_all('a')
       
        links = []
        for node in nodes_a:
            if '/ctot.php?e' in node['href']:
                links.append(node['href'])

        return links

    def scrape(self, course):
        html = self.__download(self.url + course)
        links = self.__get_links(html)

        for link in links[0:1]:  # Per capturar tots els enllaços treure l'slicing
            html = self.__download(link)
            bs = BeautifulSoup(html, "html.parser")

            # STT and ESP
            titles = bs.find_all('h1')
            title = titles[1].text.split("-")
            p = re.compile('SSTT|ESPECIALITAT|:|\s')
            sstt = p.sub('', title[0])
            esp = p.sub('', title[1])

            table = bs.find('table')
            # TODO

