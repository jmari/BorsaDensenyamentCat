import requests
import re
import time
import os
import pandas as pd
from bs4 import BeautifulSoup
from urllib import robotparser
import columnFilter as ct


class WebScraper:
    URL = "http://sindicat.net/borsa/"
    COURSES = ["1314", "1415", "1516", "1617", "1718", "1819"]
    LABELS_OLD = ['curs','sstt', 'especialitat', 'inicials', 'bloc', 'n_interi', 'data_ini',
                  'especialitat_dest', 'centre', 'tipus_jornada', 'data_fi']
    LABELS_1618 = ['curs','sstt', 'especialitat', 'inicials', 'bloc', 'n_interi', 'data_ini',
                   'tipus_jornada', 'especialitat_dest', 'codi_centre', 'centre', 'data_fi']
    LABELS_1819 = ['curs','sstt', 'especialitat', 'inicials', 'bloc', 'n_interi', 'data_ini',
                   'tipus_jornada', 'especialitat_dest', 'centre', 'data_fi']
    LABELS = ['curs','sstt', 'especialitat', 'inicials', 'bloc', 'n_interi', 'data_ini',
              'especialitat_dest', 'codi_centre', 'centre', 'tipus_jornada', 'data_fi']

    COL_TRANSFORMER_MAP = {
        'curs': ct.NullFilter() ,
        'sstt': ct.NullFilter(), 
        'especialitat': ct.NullFilter(), 
        'inicials': ct.NullFilter(), 
        'bloc': [ct.NullFilter(), ct.IntFilter()], #test de llista de filtres 
        'n_interi': ct.IntFilter().cannotBeNone(), 
        'data_ini': ct.DateFilter(),
        'especialitat_dest': ct.NullFilter(), 
        'codi_centre': ct.IntFilter(), 
        'centre':ct.NullFilter(), 
        'tipus_jornada': ct.TipusJornadaFilter(), 
        'data_fi': ct.DateFilter()}


    def __init__(self, course):
        self.data = pd.DataFrame(columns=self.LABELS)
        self.course = course
        self.rp = robotparser.RobotFileParser()
        self.rp.set_url("http://sindicat.net/robots.txt")
        self.rp.read()

    def __download(self, url):
        if self.rp.can_fetch("*", url):
            print("Downloading", url, "...")
            user_agent = {"User-agent":"UOCScraper"}
            r = requests.get(url, headers = user_agent)
            return r.text
        else:
            print("Download", url, "disallowed by robots.txt")
            return ""

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

    def __complete_date(self,raw_date,year):
        # Completa la data afegint l'any, si troba "dif" canvia per 01/01 
        try:
            year = '20'+ year
            splited_date = raw_date.split('/')
            processed_date = (splited_date[0] +'/'+ splited_date[1] + '/'+ year)
        except:
            processed_date = '01/01/'+year
        return processed_date

    def __transform_data(self):
        #Transformació de les dades
        row_transformer = ct.RowTransformer(self.data,self.COL_TRANSFORMER_MAP)
        self.data['data_ini'] = self.data['data_ini'].apply(lambda x: self.__complete_date(x,self.course[0:2]))
        self.data['data_fi'] = self.data['data_fi'].apply(lambda x: self.__complete_date(x,self.course[2:]))
        self.data = row_transformer.transform()

    def __scrape_data(self, bs):
        titles = bs.find_all('h1')
        title = titles[1].text.split("-")
        p = re.compile('SSTT|ESPECIALITAT|:|\s')
        sstt = p.sub('', title[0])
        esp = p.sub('', title[1])

        table = bs.find('table')
        for row in table.find_all('tr'):
            data_row = [self.course,sstt, esp]
            for i, cell in enumerate(row.find_all('td')[1:]): 
                data_row.extend(self.__split_columns(i, cell.text))

            if self.course =='1819':
                df = pd.DataFrame(data=[data_row], columns=self.LABELS_1819)
            elif self.course in ['1617', '1718']:
                df = pd.DataFrame(data=[data_row], columns=self.LABELS_1618)
            else:
                df = pd.DataFrame(data=[data_row], columns=self.LABELS_OLD)
                df = self.__extract_codi_centre(df)

            self.data = pd.concat([self.data,df],0, ignore_index=True, sort=True)
        self.__transform_data()



    def __scrape_course(self):
        html = self.__download(self.URL + self.course)
        links = self.__get_links(html)

        for link in links[0:2]:  # Per capturar tots els enllaços treure l'slicing
            t = time.time()
            html = self.__download(link)
            bs = BeautifulSoup(html, "html.parser")
            self.__scrape_data(bs)
            dt = time.time() - t
            time.sleep(10 * dt)

    def scrape(self):
        if self.course=="ALL":
            for course in self.COURSES:
                self.course = course
                self.__scrape_course()
            self.course = "ALL"
        else:
            self.__scrape_course()

    def get_data(self):
        return self.data

    def write_csv(self):
        outname = "dades" + self.course + ".csv"
        outdir = '../data'

        if not os.path.exists(outdir):
            os.mkdir(outdir)
        course_file = os.path.join(outdir, outname)

        self.data.to_csv(course_file, index=False, header=True, sep=';')

