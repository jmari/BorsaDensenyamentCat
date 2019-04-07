# Pràctica 1: Web scraping
# Dades anuals dels nomenaments del professorat interí i substitut a Catalunya

## Descripció
Aquesta pràctica forma part de l’assignatura _Tipologia i cicle de vida de les dades_ del _Màster en Ciència de dades_ de la Universitat Oberta de Catalunya. 

L'objectiu d'aquest treball consisteix en aplicar tècniques de _web scraping_ a la pàgina https://sindicat.net per tal de recopilar informació anual sobre la composició de la borsa de treball del Departament d'Ensenyament i els nomenaments del professorat a Catalunya. Aquest conjunt de dades vol oferir a tots els professors una informació integrada de la borsa que els pugui ajudar a prendre decisions sobre el seu futur professional.

## Integrants del grup
Aquest treball ha sigut realitzat per **Victor Boix** i **Jesús Marí**.

## Codi font 
Per a la realització de la pràctica s'ha utilitzat Python 3 amb les llibreries _requests_, _re_, _time_, _os_, _pandas_ i _BeatutifulSoup_. Els fitxers que formen el codi font són:

* _src/main.py_. Mètode principal, inicia el procés de _web scraping_ donat un curs.
* _src/scraper.py_. Conté la implementació de la classe _WebScraper_ i els mètodes encarregats de descarregar, recopilar i generar el _dataset_.

## Dataset
Totes les dades recopilades es troben disponibles en format CSV a la carpeta _data_. Es disposa d'un fitxer (_dadesYYYY.csv_) per a cada curs entre "1314" i "1819" i un fitxer _dadesALL.csv_ que integra les dades de tots els cursos.

Cada fitxer conté 12 camps descrits a continuació:

* bloc. Indica el bloc de la borsa de què forma part el professor (1 si ha treballat anteriorment al Departament i 2 si no ha treballat mai)
* centre. Nom del centre de treball de l'adjudicació.
* codi_centre. Codi de 8 xifres que identifica a cada centre.
* curs. Curs escolar al què correspon el registre (per exemple: 1819).
* data_fi. Data de finalització del nomenament.
* data_ini. Data d'inici del nomenament.
* especialitat. Codi de l'especialitat sol·licitada pel professor format per 2 o 3 dígits.
* especialitat_dest. Codi de l'especialitat per a la qual ha sigut nomenat un professor.
* inicials. Inicials del professor.
* n_interi. Número d'ordre de tot professorat a la borsa de treball en funció de tot el temps treballat.
* sstt. Servei territorial preferent per al qual s'opta a treballar.
* tipus_jornada. Durada de la jornada de treball adjudicada (1 sencera, 0'5 mitja, 0'33 terç...)


## Recursos

* SUBIRATS, L.; CALVO, M. (2018). _Web Scraping_. Editorial UOC.
* LAWSON, R. (2015). _Web Scraping with Python_. Packt Publishing Ltd.
