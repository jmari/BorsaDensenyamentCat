from datetime import date
import re

class NullFilter:
   
    def __init__(self,col_name=''):
        self.canBeNone = True
        self.column_name = col_name
        self.transform_function = lambda x: x 

    def setColumnName(self, col_name):
        self.column_name=col_name
        return (self)
    
    def cannotBeNone(self):
        self.canBeNone = False
        return (self)
    
 
    def transform(self, raw_val):
        if not self.canBeNone and (raw_val is None or not raw_val):
            raise Exception('{} should not be None'.format(self.column_name))
        if raw_val is None or not raw_val:
            return (raw_val)
        return (self.transform_function(raw_val))
    


class DateFilter(NullFilter):
    #Filtre per a les columnes amb dates, s'ha d'indicar l'any 
    def __init__(self):
        super(DateFilter, self).__init__()
        self.transform_function = self.__transform_date

    def __transform_date(self, raw_date):
        splited_date = raw_date.split('/')
        transformed_date = date(int(splited_date[2]),int(splited_date[1]),int(splited_date[0]))
        return(transformed_date)


class IntFilter(NullFilter):
    #Filtre per a les columnes amb enters, neteja tots els caracters no vàlids
    def __init__(self):
        super(IntFilter, self).__init__()
        self.transform_function = self.__transform_integer
    
    def __transform_integer(self, raw_integer):
        try:
            return(re.sub('[^0-9]','', raw_integer))
        except:
            return(None)


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
    def __init__(self, dataframe, col_trf_map):
        self.dataframe = dataframe
        self.col_trf_map = col_trf_map

    def __apply_all_filters(self, raw_data,col_name, list_of_filters):
        filtered_data = raw_data
        for filter in list_of_filters:
            filter.setColumnName(col_name)
            filtered_data =  filter.transform(filtered_data)
        return (filtered_data)

    def transform(self):
        #transforma el dataframe i el retorna transformat
        for col, filter in self.col_trf_map.items():
            #filter pot ser un filtre o una llista de filtres
            if type(filter) is list:
                self.dataframe[col] = self.dataframe[col].apply(lambda x:self.__apply_all_filters(x,col, filter))
            else:
                filter.setColumnName(col)
                self.dataframe[col] = self.dataframe[col].apply(lambda x:filter.transform(x))

        return (self.dataframe)
            
