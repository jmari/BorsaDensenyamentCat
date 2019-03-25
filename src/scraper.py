import requests
import re
import time
import csv
from bs4 import BeautifulSoup


class WebScraper:

    def __init__(self):
        self.url = "http://sindicat.net/borsa/"
        self.data = []

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
   

    def __split_columns(self, index, text):
        converter = lambda x: x.replace('\xa0',' ').replace('- FITXA','').strip(' ') 
        if index == 0 or index == 1:
            columns = text.rsplit(" ",2)
            fields = [ converter(a_field) for a_field in columns]
        else:
            fields = [converter(text)]
        return fields


    def __scrape_data(self, bs):
        titles = bs.find_all('h1')
        title = titles[1].text.split("-")
        p = re.compile('SSTT|ESPECIALITAT|:|\s')
        sstt = p.sub('', title[0])
        esp = p.sub('', title[1])

        table = bs.find('table')
        for row in table.find_all('tr'):
            data_row = [sstt, esp]
            for i, cell in enumerate(row.find_all('td')[1:]): 
                data_row.extend(self.__split_columns(i, cell.text))
            if len(data_row) == 11:
                data_row[9] = data_row[6]
                del data_row[6] 

            #SALIDA PARA DEBUG----CHEQUEO LONGITUD Y CONTENIDO    
            print(len(data_row))    
            print(data_row,end='\n')
            self.data.append(data_row)

    def __write_csv(self, filename):
        with open("../data/" + filename, 'w', newline="") as csvfile:
            w = csv.writer(csvfile, delimiter=";", quotechar="|", quoting=csv.QUOTE_MINIMAL)
            for x in self.data:
                w.writerow(x)

    def scrape(self, course):
        html = self.__download(self.url + course)
        links = self.__get_links(html)

        for link in links[0:3]:  # Per capturar tots els enllaços treure l'slicing
            t = time.time()
            html = self.__download(link)
            bs = BeautifulSoup(html, "html.parser")
            self.__scrape_data(bs)
            dt = time.time() - t
            time.sleep(10 * dt)

        self.__write_csv("dades" + course + ".csv")

