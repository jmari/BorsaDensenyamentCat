import requests
import re
import time
import os
import pandas as pd
import columnFilter as ct
from bs4 import BeautifulSoup
from urllib import robotparser



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
        'bloc': ct.IntFilter(), #test de llista de filtres 
        'n_interi': ct.IntFilter().cannotBeNone(), 
        'data_ini': [ct.PointPerBarFilter(), ct.DataFilterIni()],
        'especialitat_dest': ct.NullFilter(), 
        'codi_centre': ct.IntFilter(), 
        'centre':ct.NullFilter(), 
        'tipus_jornada': ct.TipusJornadaFilter(), 
        'data_fi': [ct.PointPerBarFilter(), ct.DataFilterIni()]}

    # Maxim nombre d'intents de descarrega
    MAX_DOWNLOAD_ERROR = 3

    def __init__(self, course):
        # dataframe que emmagatzema les dades capturades
        self.data = pd.DataFrame(columns=self.LABELS)

        # curs a rastrejar
        self.course = course

        # comprovació del fitxer robots.txt
        self.rp = robotparser.RobotFileParser()
        self.rp.set_url("http://sindicat.net/robots.txt")
        self.rp.read()

        # Si la descarrega falla torna a intentar fins a MAX_DOWNLOAD_ERRORS
        self.download_errors = 0

    def __download(self, url):
        # Descarrega una pàgina a partir de la URL
        # retorna un string amb el codi html

        if self.rp.can_fetch("*", url):  # Comprova el fitxer robots.txt
            print("Downloading", url, "...")
            user_agent = {"User-agent":"UOCScraper"}
            try:
                r = requests.get(url, headers = user_agent)
                self.download_errors = 0
            except:
                self.download_errors += 1
                if self.download_errors < self.MAX_DOWNLOAD_ERROR:
                    print ("Esperant 10s per connexió"  )
                    time.sleep(10.0)
                    return (self.__download(url))
                else:
                    self.download_errors = 0
                    raise Exception("Superat maxim nombre d'intents de descarrega")
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


    def __transform_data(self, df):
        #Transformació de les dades
        row_transformer = ct.RowTransformer(df,self.COL_TRANSFORMER_MAP)
        return (row_transformer.transform())

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
            
            self.data = pd.concat([self.data,self.__transform_data(df)],0, ignore_index=True, sort=False)
        print ("Files filtrades i afegides. Les dimensions del DF: "+ str(self.data.shape))    


    def __scrape_course(self):
        # Captura totes les dades del curs especificat a l'atribut "course"

        # Genera la URL i obté tots els enllaços
        html = self.__download(self.URL + self.course)
        links = self.__get_links(html)

        # Recorre tots els enllaços i en captura el contingut
        for link in links: # [0:5]:  Per capturar tots els enllaços treure l'slicing
            try:
                t = time.time()
                html = self.__download(link)  # descarrega la URL
                dt = time.time() - t
                bs = BeautifulSoup(html, "html.parser")  # parseja el contingut 
                self.__scrape_data(bs)  # Captura les dades
            except Exception as e:
                print("excepcio extraient data del link " +link +" " + str(e))

            print ("Esperant: " + str(2*dt)  )
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

