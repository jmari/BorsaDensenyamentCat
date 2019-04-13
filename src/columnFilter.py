from datetime import date
import re
import pandas as pd
from datetime import datetime

class NullFilter:
   
    def __init__(self,col_name=''):
        self.canBeNone = True
        self.column_name = col_name
        self.current_row = None
        self.transform_function = lambda x: x 

    def setColumnName(self, col_name):
        # nom de la column, la classe rowTransformer inicialitza el nom abanç d'executar transform
        self.column_name=col_name
        return (self)

    def setCurrentRow(self, current_row):
        # actualitza current_row, la classe rowTransformer inicialitza el current_row abanç d'executar transform
        self.current_row = current_row
        return (self)
    
    def cannotBeNone(self):
        # Si activem aquesta opcio  i el valor es none o un string buit emetra una Excepcio
        self.canBeNone = False
        return (self)
    
 
    def transform(self, raw_val):
        if not self.canBeNone and (raw_val is None or not raw_val):
            raise Exception('{} should not be None'.format(self.column_name))
        if raw_val is None or not raw_val:
            return (raw_val)
        try:
            return (self.transform_function(raw_val))
        except:
            print('error filtrant columna: '+ self.column_name+'am valor:' + str(raw_val))
            return None

class PointPerBarFilter(NullFilter):
    #Filtre per a les columnes amb dates canvia format dd.mm per dd/mm
    def __init__(self):
        super(PointPerBarFilter, self).__init__()
        self.transform_function = self.__transform_date
    def __transform_date(self, raw_date):
        return (raw_date.replace(".","/"))
         

class DataFilterIni(NullFilter):
    #Filtre per a les columnes amb dates d'inici, obté l'any de la columna curs
    def __init__(self):
        super(DataFilterIni, self).__init__()
        self.transform_function = self.__transform_date

    def __transform_date(self, raw_date):
        
        splited_date = raw_date.split('/')
        year = "20" + self.current_row['curs'][0:2]
        if splited_date[1] in ["01","02","03","04","05","06"]:
            year = "20" + self.current_row['curs'][2:]
        transformed_date = date(int(year),int(splited_date[1]),int(splited_date[0]))
        return(transformed_date)


class DataFilterFi(NullFilter):
    # Filtre per a les columnes amb dates de finalització, obté l'any de la columna curs
    def __init__(self):
        super(DataFilterFi, self).__init__()
        self.transform_function = self.__transform_date

    def __transform_date(self, raw_date):
        splited_date = raw_date.split('/')
        year = "20" + self.current_row['curs'][0:2]
        if splited_date[1] in ["01","02","03","04","05","06","07","08"]:
            year = "20" + self.current_row['curs'][2:]
        transformed_date = date(int(year), int(splited_date[1]), int(splited_date[0]))
        return (transformed_date)


class IntFilter(NullFilter):
    #Filtre per a les columnes amb enters, neteja tots els caracters no vàlids
    def __init__(self):
        super(IntFilter, self).__init__()
        self.transform_function = self.__transform_integer
    
    def __transform_integer(self, raw_integer):
        return(re.sub('[^0-9]','', raw_integer))
        


class TipusJornadaFilter(NullFilter):
    #Filtre per a la columna tipus_jornada, normalment és un float, però apareixen textes com ara mitja...
    def __init__(self):
        super(TipusJornadaFilter, self).__init__()
        self.transform_function = self.__transform_tipus_jornada

    def __transform_tipus_jornada(self, raw_tipus_jornada):
        if raw_tipus_jornada =='mitja':
            return(0.5)
        tr_tipus_jornada = raw_tipus_jornada if type(raw_tipus_jornada) is float else raw_tipus_jornada.replace(',','.')
        try:
            tipus_jornada = float(tr_tipus_jornada)
        except:
            print('error filtrant columna tipus_jornada amb valor: ' + tr_tipus_jornada+ ' per defecte 1')
            tipus_jornada = 1.0
        return (tipus_jornada)
        


class RowTransformer:
    # Classe per a netejar i transformar els dataframes. Al constructor li passem el df
    # a més d'un diccionari amb columna:instancia de filtre que anirá aplicant a tots els valors
    # a la instancia de filtre li podem passar una llista de filtres per aplicar succesivament
    
    def __init__(self, dataframe, col_trf_map):
        self.dataframe = dataframe
        self.col_trf_map = col_trf_map

    def __apply_all_filters(self, raw_data,col_name, list_of_filters,current_row):
        filtered_data = raw_data
        for filter in list_of_filters:
            filter.setColumnName(col_name)
            filter.setCurrentRow(current_row)
            filtered_data =  filter.transform(filtered_data)
        return (filtered_data)

    def transform(self):
        #crea un nou dataframe amb l'aplicació dels filtres a cada valor raw
        new_dataframe = pd.DataFrame(columns=self.dataframe.columns.values, index=self.dataframe.index.values)
        for index, row in self.dataframe.iterrows():
            new_row = {}
            for col, filter in self.col_trf_map.items():
                if col in row.keys():
                    if type(filter) is list:
                        new_row[col] = self.__apply_all_filters(row[col],col, filter,row)
                    else:
                        filter.setColumnName(col)
                        filter.setCurrentRow(row)
                        new_row[col] =  filter.transform(row[col])
            new_dataframe.iloc[index]=new_row
        return (new_dataframe)
            
