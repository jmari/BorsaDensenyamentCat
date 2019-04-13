# Dades anuals dels nomenaments del professorat interí i substitut a Catalunya

![Cua de professors](./docs/PRA1_Borsa.jpg)

## Descripció
Aquesta pràctica forma part de l’assignatura _Tipologia i cicle de vida de les dades_ del _Màster en Ciència de dades_ de la Universitat Oberta de Catalunya. 

L'objectiu d'aquest treball consisteix en aplicar tècniques de _web scraping_ a la pàgina https://sindicat.net per tal de recopilar informació anual sobre la composició de la borsa de treball del Departament d'Ensenyament i els nomenaments del professorat a Catalunya. Aquest conjunt de dades vol oferir a tots els professors una informació integrada de la borsa que els pugui ajudar a prendre decisions sobre el seu futur professional.

## Integrants del grup
Aquest treball ha sigut realitzat per **Victor Boix** i **Jesús Marí**.

## Codi font 
Per a la realització de la pràctica s'ha utilitzat Python 3 amb les llibreries _requests_, _re_, _time_, _os_, _pandas_ i _BeatutifulSoup_. Els fitxers que formen el codi font són:

* **main.py** - Mètode principal, inicia el procés de web scraping donat un curs.
* **scraper.py** - Conté la implementació de la classe WebScraper i els mètodes encarregats de descarregar, recopilar i generar el dataset.
* **columnFilter.py** - Conté diferents classes que actuen de filtres per a la neteja de dades dels diferents camps del dataset.

## Dataset
El conjunt de dades està format per 6 datasets corresponents a les dades de cada curs escolar entre 2013 i 2019. 
Aquests datasets es troben a la carpeta _data_ en format CSV i s'anomenen _dadesyyYY.csv_, on yy és l'any d'inici de curs i YY l'any de finalització (per exemple dades1819.csv conté les dades del curs 2018-2019). 
A més, el codi també permet capturar totes les dades en un únic dataset anomenat _dadesALL.csv_ que engloba la informació de tots els cursos.
Cada dataset conté un registre per a cada professor que opta a un lloc de treball per a una especialitat concreta a un servei territorial. 
Cada registre conté informació sobre el curs, el número de la borsa que identifica al treballador, l'especialitat demanada i el servei territorial preferent. 
A més, per als professors que ja han sigut nomenats, es disposa d'informació sobre l'adjudicació: especialitat, jornada, centre, dates d'inici i finalització.

Cada fitxer conté 12 camps descrits a continuació:

* **curs** (*integer*). Curs escolar al què correspon el registre seguint el format yyYY (per exemple: 1819).
* **sstt** (*integer*). Codi numèric del servei territorial preferent (zona) per al qual s'opta a treballar.
* **especialitat** (*string*). Codi de l'especialitat docent sol·licitada pel professor, format per 2 o 3 dígits.
* **inicials** (*string*). Inicials del professor. Tres lletres, per exemple CC, N.
* **bloc** (*integer*). Indica el bloc de la borsa de què forma part el professor (1 si ha treballat anteriorment al Departament i 2 si no ha treballat mai).
* **n_interi** (*integer*). Número d'ordre de tot el professorat a la borsa de treball en funció del temps treballat.
* **data_ini** (*date*). Data d'incorporació al centre en format dd/mm/yyyy.
* **especialitat_dest** (*string*). Codi de l'especialitat docent per a la qual ha sigut nomenat un professor (2 o 3 dígits).
* **codi_centre** (*integer*). Codi de 8 xifres que identifica a cada centre de manera única.
* **centre** (*string*). Nom del centre de treball de l'adjudicació.
* **tipus_jornada** (*float*). Durada de la jornada de treball adjudicada (1 sencera, 0'5 mitja, 0'33 terç...).
* **data_fi** (*date*). Data de finalització del nomenament en format dd/mm/yyyy.


## Recursos

* SUBIRATS, L.; CALVO, M. (2018). _Web Scraping_. Editorial UOC.
* LAWSON, R. (2015). _Web Scraping with Python_. Packt Publishing Ltd.
