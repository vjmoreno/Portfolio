from Segmentacion import Segmentacion
from Procesamiento_horero_minutero import Procesamiento_horero_minutero
from Procesamiento_segundero import Procesamiento_segundero
from Calcular_hora import Calcular_hora

class Procesamiento:

    def __init__(self, filename):
        'Clase destinada a entregar el resultado del proceso'
        #nombre de la foto
        self.filename = filename
        self.segmentacion = Segmentacion(self.filename)
        # Realizamos la segmentacion
        self.segmentacion.realizar_segmentacion()
        self.p_horero_minutero = Procesamiento_horero_minutero(self.filename)
        #Realizamos el procesamiento previo a encontrar las manecillas
        self.p_horero_minutero.realizar_procesamiento()
        #Obtenemos el angulo del minutero
        self.angulo_minutero = self.p_horero_minutero.buscar_minutero()
        #Obtenemos el angulo del horero
        self.angulo_horero = self.p_horero_minutero.buscar_horero()
        self.p_segundero = Procesamiento_segundero(self.filename, self.angulo_horero, self.angulo_minutero, self.p_horero_minutero.centro)
        #Obtenemos el angulo del segundero
        self.angulo_segundero = self.p_segundero.realizar_procesamiento()
        self.calcular_hora = Calcular_hora(self.angulo_horero, self.angulo_minutero, self.angulo_segundero)
        #Calculamos la hora
        self.calcular_hora.calcular_hora()


#Introducir el nombre de la imagen a trabajar.
P = Procesamiento('./relojes/IMG_2318.JPG')
