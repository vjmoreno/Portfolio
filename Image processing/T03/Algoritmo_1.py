import cv2
import numpy as np
from random import randrange
from matplotlib import pyplot as plt


class Algoritmo_1:

    def __init__(self, filename):
        '''Se lee la imagen y se reordenan los valores de los pixeles de la imagen para evitar problemas
        al graficarla, puesto que una vez abierta una imagen con el metodo cv2.imread() los valores de
        cada pixel estan ordenados de la siguiente forma: blue, green, red'''
        self.bgr_img = cv2.imread('./FOTOS_ALGORITMO_1/{}'.format(filename))
        # se obtienen los valores
        self.b,self.g,self.r = cv2.split(self.bgr_img)
        # se reordenan los valores
        self.rgb_img = cv2.merge([self.r,self.g,self.b])
        self.lista_colores = []

    def run(self):
        ''' Se realizan todas las acciones necesarias para obtener la imagen deseada y luego graficarla '''
        self.canny = self.auto_canny(self.rgb_img)
        # Se elimina el ruido de la imagen
        self.rgb_img = cv2.fastNlMeansDenoisingColored(self.rgb_img,None,10,10,7,21)
        # Se utiliza un filtro de mediana de tamano 5
        self.rgb_img = cv2.medianBlur(self.rgb_img,5)
        self.escoger_colores()
        self.cambiar_colores()
        plt.imshow(self.rgb_img)
        plt.show()

    def escoger_colores(self):
        ''' Se realiza un loop de 50 iteraciones con el objetivo de escoger los colores que
        conformaran la imagen final'''
        for number in range(50):
            # Se escoge al azar un pixel
            x = randrange(self.rgb_img.shape[1])
            y = randrange(self.rgb_img.shape[0])
            # Valores RGB del pixel
            r, g, b = self.rgb_img[y, x]
            # Si la lista de colores esta vacia simplemente se agrega el color
            if len(self.lista_colores) == 0:
                self.lista_colores.append(Color(r,g,b))
            else:
                # En caso contrario el color sera escogido solo si cumple con la condicion de que la distancia
                # entre este color y el resto de colores de la lista es mayor a 30
                bool = True
                for color in self.lista_colores:
                    # calculo de la distancia entre 2 colores
                    distancia = self.distancia(color, r, g, b)
                    if distancia < 30:
                        bool = False
                if bool:
                    self.lista_colores.append(Color(r,g,b))

    def cambiar_colores(self):
        ''' Se cambia el color de cada pixel por un promedio entre los valores RGB del color
         de la lista_colores con el que tenga una menor distancia y sus propios valores'''
        #Loop que recorre toda la imagen
        for x in range(self.rgb_img.shape[1]):
            for y in range(self.rgb_img.shape[0]):
                #valores RGB del pixel
                r, g, b = self.rgb_img[y, x]
                #diccionario con distancia:color entre el color del pixel y cada uno de los colores de la lista_colores
                dict_distancia = {self.distancia(color, r, g, b): color for color in self.lista_colores}
                # Se busca la minima distancia
                dist_min = min(dict_distancia.items(), key=lambda x: x[0])[0]
                # Se obtiene el color
                color = dict_distancia[dist_min]
                if self.canny[y,x] == 255:
                    # Si el color el blanco en la imagen canny se le resta 10 a cada valor promedio
                    self.rgb_img[y, x]= [max(int((int(color.r)+int(r))/2)-10, 0),max(int((int(color.g)+int(g)))/2-10, 0), max(int((int(color.b)+int(b))/2)-10, 0)]
                else:
                    # El color final es el promedio entre el color encontrado y los valores propios del pixel
                    self.rgb_img[y, x]= [int((int(color.r)+int(r))/2),int((int(color.g)+int(g)))/2, int((int(color.b)+int(b))/2)]


    def distancia(self, color, r, g, b):
        # Definicion de distancia entre dos colores
        return ((int(color.r) - int(r))**2 + (int(color.g) - int(g))**2 + (int(color.b) - int(b))**2)**0.5


    def auto_canny(self, image, sigma=0.33):
        # Metodo utilizado para obtener la imagen canny con los bordes de la imagen original
        v = np.median(image)
        lower = int(max(0, (1.0 - sigma) * v))
        upper = int(min(255, (1.0 + sigma) * v))
        edged = cv2.Canny(image, lower, upper)
        return edged


class Color:

    def __init__(self, r, g, b):
        self.r = r
        self.g = g
        self.b = b

A = Algoritmo_1('13014286635_ce2d955f04_z.JPG')
A.run()