from datetime import date
import re

class NullTransformer:
   
    def __init__(self,col_name=''):
        self.canBeNone = True
        self.column_name = col_name
        self.transform_function = lambda x: x 

    def setColumnName(self, col_name):
        self.column_name=col_name
        return (self)
    
    def canNotBeNone(self):
        self.canBeNone = False
        return (self)
    
 
    def transform(self, raw_val):
        if not self.canBeNone and (raw_val is None or not raw_val):
            raise Exception('{} should not be None'.format(self.column_name))
        if raw_val is None or not raw_val:
            return (raw_val)
        return (self.transform_function(raw_val))
    


class DateTransformer(NullTransformer):
    #Filtre per a les columnes amb dates, s'ha d'indicar l'any 
    def __init__(self):
        super(DateTransformer, self).__init__()
        self.transform_function = self.__transform_date

    def __transform_date(self, raw_date):
        splited_date = raw_date.split('/')
        transformed_date = date(int(splited_date[2]),int(splited_date[1]),int(splited_date[0]))
        return(transformed_date)


class IntTransformer(NullTransformer):
    #Filtre per a les columnes amb enters, neteja tots els caracters no vàlids
    def __init__(self):
        super(IntTransformer, self).__init__()
        self.transform_function = self.__transform_integer
    
    def __transform_integer(self, raw_integer):
        try:
            return(re.sub('[^0-9]','', raw_integer))
        except:
            return(None)


class TipusJornadaTransformer(NullTransformer):
    #Filtre per a la columna tipus_jornada, normalment és un float, però apareixen textes com ara mitja...
    def __init__(self):
        super(TipusJornadaTransformer, self).__init__()
        self.transform_function = self.__transform_tipus_jornada

    def __transform_tipus_jornada(self, raw_tipus_jornada):
        if raw_tipus_jornada =='mitja':
            return(0.5)
        tr_tipus_jornada = raw_tipus_jornada if type(raw_tipus_jornada) is float else raw_tipus_jornada.replace(',','.')
        try:
            tipus_jornada = float(tr_tipus_jornada)
        except:
            print('error transformant columna tipus_jornada amb valor: ' + tr_tipus_jornada+ ' per defecte 1')
            tipus_jornada = 1.0
        return (tipus_jornada)
        


class RowTransformer:
    def __init__(self, dataframe, col_trf_map):
        self.dataframe = dataframe
        self.col_trf_map = col_trf_map

    def transform(self):
        #transforma el dataframe i el retorna transformat
        for col, transformer in self.col_trf_map.items():
            transformer.setColumnName(col)
            self.dataframe[col] = self.dataframe[col].apply(lambda x:transformer.transform(x))
        return (self.dataframe)
            
