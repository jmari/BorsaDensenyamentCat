import requests
import re
import time
import csv
import pandas as pd
from bs4 import BeautifulSoup



class WebScraper:

    URL = "http://sindicat.net/borsa/"
    LABELS_OLD = ['sstt', 'especialitat', 'inicials', 'bloc', 'n_interi', 'data_ini',
                       'especialitat_dest', 'centre', 'tipus_jornada', 'data_fi']
    LABELS_1618 = ['sstt', 'especialitat', 'inicials', 'bloc', 'n_interi', 'data_ini',
                        'tipus_jornada', 'especialitat_dest', 'codi_centre','centre', 'data_fi']
    LABELS_1819 = ['sstt', 'especialitat', 'inicials', 'bloc', 'n_interi', 'data_ini',
                        'tipus_jornada', 'especialitat_dest', 'centre', 'data_fi']
    LABELS = ['sstt', 'especialitat', 'inicials', 'bloc', 'n_interi', 'data_ini',
                   'especialitat_dest', 'codi_centre', 'centre', 'tipus_jornada', 'data_fi']

    def __init__(self):
        self.data = pd.DataFrame(columns=self.LABELS)

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
        converter = lambda x: x.replace('\xa0',' ').replace('- FITXA','').replace('(*)','').strip(' ')
        if index == 0 or index == 1:
            columns = text.rsplit(" ",2)
            fields = [ converter(a_field) for a_field in columns]
        else:
            fields = [converter(text)]

        return fields

    def __extract_codi_centre(self, df):
        # Extreu el codi de centre del camp "centre"
        p = re.compile('[0-9]{8}')
        centre = df['centre'].values[0]
        if p.match(centre):
            df['codi_centre'] = p.findall(centre)[0]
            df['centre'] = p.sub('',centre)

        return df

    def __scrape_data(self, bs, course):
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

            if course =='1819':
                df = pd.DataFrame(data=[data_row], columns=self.LABELS_1819)
            elif course in ['1617', '1718']:
                df = pd.DataFrame(data=[data_row], columns=self.LABELS_1618)
            else:
                df = pd.DataFrame(data=[data_row], columns=self.LABELS_OLD)
                df = self.__extract_codi_centre(df)

            self.data = pd.concat([self.data,df],0, ignore_index=True, sort=True)
    '''
    def __write_csv(self, filename):
        with open("../data/" + filename, 'w', newline="") as csvfile:
            w = csv.writer(csvfile, delimiter=";", quotechar="|", quoting=csv.QUOTE_MINIMAL)
            for x in self.data:
                w.writerow(x)
    '''
    def scrape(self, course):
        html = self.__download(self.URL + course)
        links = self.__get_links(html)

        for link in links[0:3]:  # Per capturar tots els enllaços treure l'slicing
            t = time.time()
            html = self.__download(link)
            bs = BeautifulSoup(html, "html.parser")
            self.__scrape_data(bs, course)
            dt = time.time() - t
            time.sleep(10 * dt)

        return self.data
        #self.__write_csv("dades" + course + ".csv")

