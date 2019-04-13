import requests
import re
import time
import os
import pandas as pd
from bs4 import BeautifulSoup
from urllib import robotparser
import columnFilter as ct


class WebScraper:
    # Enllaç base de les pàgines a rastrejar
    URL = "http://sindicat.net/borsa/"

    # Cursos disponibles a la web
    COURSES = ["1314", "1415", "1516", "1617", "1718", "1819"]

    # Camps disponibles a cada curs en l'ordre correcte
    LABELS_OLD = ['curs','sstt', 'especialitat', 'inicials', 'bloc', 'n_interi', 'data_ini',
                  'especialitat_dest', 'centre', 'tipus_jornada', 'data_fi']
    LABELS_1618 = ['curs','sstt', 'especialitat', 'inicials', 'bloc', 'n_interi', 'data_ini',
                   'tipus_jornada', 'especialitat_dest', 'codi_centre', 'centre', 'data_fi']
    LABELS_1819 = ['curs','sstt', 'especialitat', 'inicials', 'bloc', 'n_interi', 'data_ini',
                   'tipus_jornada', 'especialitat_dest', 'centre', 'data_fi']

    # Nom de les columnes del dataframe final
    LABELS = ['curs','sstt', 'especialitat', 'inicials', 'bloc', 'n_interi', 'data_ini',
              'especialitat_dest', 'codi_centre', 'centre', 'tipus_jornada', 'data_fi']

    # Diccionari amb els filtres de cada atribut
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
        # dataframe que emmagatzema les dades capturades
        self.data = pd.DataFrame(columns=self.LABELS)

        # curs a rastrejar
        self.course = course

        # comprovació del fitxer robots.txt
        self.rp = robotparser.RobotFileParser()
        self.rp.set_url("http://sindicat.net/robots.txt")
        self.rp.read()

    def __download(self, url):
        # Descarrega una pàgina a partir de la URL
        # retorna un string amb el codi html

        if self.rp.can_fetch("*", url):  # Comprova el fitxer robots.txt
            print("Downloading", url, "...")
            user_agent = {"User-agent":"UOCScraper"}
            r = requests.get(url, headers = user_agent)
            return r.text
        else:
            print("Download", url, "disallowed by robots.txt")
            return ""

    def __get_links(self, html):
        # Obté tots els enllaços amb dades donat el codi html d'una pàgina
        # retorna un array amb els enllaços

        bs = BeautifulSoup(html, "html.parser")
        nodes_a = bs.find_all('a')
       
        links = []
        for node in nodes_a:
            if '/ctot.php?e' in node['href']:
                links.append(node['href'])
        return links

    def __split_columns(self, index, text):
        # Separa el contingut de les cel·les que contenen més d'una dada

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

    def __complete_date_ini(self,raw_date,course):
        # Completa la data d'inici afegint l'any

        try:
            year = "20" + course[0:2]
            splited_date = raw_date.split('/')
            if splited_date[1] in ["01","02","03","04","05","06"]:
                year = "20" + course[2:]
            processed_date = (splited_date[0] +'/'+ splited_date[1] + '/'+ year)
            return processed_date
        except:
            return None

    def __complete_date_fi(self,raw_date,course):
        # Completa la data de finalització afegint l'any

        try:
            year = "20" + course[2:]
            splited_date = raw_date.split('/')
            if splited_date[1] in ["09","10","11","12"]:
                year = "20" + course[0:2]
            processed_date = (splited_date[0] +'/'+ splited_date[1] + '/'+ year)
            return processed_date
        except:
            return None

    def __transform_data(self):
        #Transformació de les dades

        row_transformer = ct.RowTransformer(self.data,self.COL_TRANSFORMER_MAP)
        self.data['data_ini'] = self.data['data_ini'].apply(lambda x: self.__complete_date_ini(x,self.course))
        self.data['data_fi'] = self.data['data_fi'].apply(lambda x: self.__complete_date_fi(x,self.course))
        self.data = row_transformer.transform()

    def __scrape_data(self, bs):
        # Captura les dades d'una pàgina i les guarda a l'atribut data

        # Captura el servei territorial i l'especialitat del títol
        titles = bs.find_all('h1')
        title = titles[1].text.split("-")
        p = re.compile('SSTT|ESPECIALITAT|:|\s')
        sstt = p.sub('', title[0])
        esp = p.sub('', title[1])

        # Captura les dades de la taula
        table = bs.find('table')
        for row in table.find_all('tr'):
            data_row = [self.course,sstt, esp]
            for i, cell in enumerate(row.find_all('td')[1:]): 
                data_row.extend(self.__split_columns(i, cell.text))

            # El nombre i ordre dels camps depenen del curs
            if self.course =='1819':
                df = pd.DataFrame(data=[data_row], columns=self.LABELS_1819)
            elif self.course in ['1617', '1718']:
                df = pd.DataFrame(data=[data_row], columns=self.LABELS_1618)
            else:
                df = pd.DataFrame(data=[data_row], columns=self.LABELS_OLD)
                df = self.__extract_codi_centre(df)

            self.data = pd.concat([self.data,df],0, ignore_index=True, sort=False)
        self.__transform_data()



    def __scrape_course(self):
        # Captura totes les dades del curs especificat a l'atribut "course"

        # Genera la URL i obté tots els enllaços
        html = self.__download(self.URL + self.course)
        links = self.__get_links(html)

        # Recorre tots els enllaços i en captura el contingut
        for link in links[0:5]:  # Per capturar tots els enllaços treure l'slicing
            t = time.time()
            html = self.__download(link)  # descarrega la URL
            dt = time.time() - t
            bs = BeautifulSoup(html, "html.parser")  # parseja el contingut
            self.__scrape_data(bs)  # Captura les dades
            time.sleep(2 * dt)  # Temps d'espera per evitar sobrecarregar el servidor

    def scrape(self):
        # Mètode públic que rastreja les dades del curs especificat a la classe

        # El paràmetre ALL captura les dades de tots els cursos
        if self.course=="ALL":
            for course in self.COURSES:
                self.course = course
                self.__scrape_course()
            self.course = "ALL"
        else:
            self.__scrape_course()

    def get_data(self):
        # Permet obtenir el contingut de l'atribut data
        # Retorna totes les dades capturades en un dataframe

        return self.data

    def write_csv(self):
        # Guarda les dades en un fitxer CSV

        outname = "dades" + self.course + ".csv"
        outdir = '../data'

        if not os.path.exists(outdir):
            os.mkdir(outdir)
        course_file = os.path.join(outdir, outname)

        self.data.to_csv(course_file, index=False, header=True, sep=';')

