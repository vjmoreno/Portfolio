__author__ = 'vjmoreno'
import numpy as np
import scipy.misc
import os
from scipy import ndimage
from PIL import Image
from matplotlib import pyplot as plt


class Segmentacion:

    def __init__(self, filename):
        self.filename = filename
        self.imagen = Image.open(self.filename)

    def realizar_segmentacion(self):
        self.calcular_promedio()
        self.eliminar_sombra()
        self.filtro_pasabajos()
        self.restar_minimo_fila()
        self.imagen_binaria()


    def calcular_promedio(self):
        '''Se calcula el promedio de los colores de las primeras 50
        lineas de pixelespara posteriormente aplicar un filtro pasabajos'''
        total = [0,0,0]
        pixels = 0
        for x in range(0,50):
            for y in range(0,self.imagen.size[1]):
                pixels += 1
                total = list(map(lambda x,y : x+y, total, list(self.imagen.getpixel((x,y))))) #se van sumando los colores RGB
        self.avg = list(map(lambda x : int(x/pixels), total)) #se divide por el total de pixeles para obtener el promedio

    def filtro_pasabajos(self):
        ''' Se aplica un fitro pasabajos a los pixeles que esten
         dentro de un rango mas o menos parecido al promedio de
        color de las 50 primeras filas de la imagen. Esto tiene
        como obtetivo evitar los pequeñas puntos blancos que quedan
         dentro de una imagen binaria cuando se utiliza otsu'''
        data = self.imagen.load()
        for x in range(0,self.imagen.size[0]):
            for y in range(0,self.imagen.size[1]):
                aux = 0
                #Se itera sobre los 3 colores rojo-verde-azul
                for number in range(3):
                    if  self.avg[number] - 40 < data[x,y][number] < self.avg[number] + 40: # rango de color
                        aux+=1
                #Si los 3 colores estan dentro del rango
                if aux == 3:
                    if (0 < x < self.imagen.size[0] - 1) and (0 < y < self.imagen.size[1] - 1):
                        #Lista con color del pixel central y de sus vecinos
                        n = [data[x-1,y-1],data[x-1,y], data[x,y-1], data[x,y], data[x+1,y+1], data[x+1,y], data[x,y+1], data[x+1,y-1], data[x-1,y+1]]
                        #Se suman los colores
                        s = [sum(i) for i in zip(*n)]
                        #Se divide por 9
                        r = tuple(map(lambda x: round(x/9), s))
                        #Se define el color
                        data[x,y] = r
        plt.imshow(self.imagen.rotate(-90))
        plt.title('IMAGEN CON FILTRO PASABAJOS EN EL FONDO CAFE')
        plt.show()

    def eliminar_sombra(self):
        ''' Metodo encargado de eliminar la sombra existente
         en la parte superior del reloj para posteriormente
         realizar otsu de mejor manera'''
        data = self.imagen.load()
        #Se recorre la imagen completa
        for x in range(0,self.imagen.size[0]):
            for y in range(0,self.imagen.size[1]):
                #Rango de color
                if (160 < data[x,y][0] < 200) and (160 < data[x,y][1] < 200) and (160 < data[x,y][2] < 200):
                    #Si esta dentro de ese rango de colores, el pixel se transforma a blanco
                    data[x,y] = (256,256,256)
        plt.imshow(self.imagen.rotate(-90))
        plt.title('IMAGEN CON SOMBRA DEL RELOJ ELIMINADA')
        plt.show()

    def restar_minimo_fila(self):
        '''Metodo que resta el minimo color de la fila a cada pixel'''
        #se itera en x
        for x in range(0,self.imagen.size[0]):
            _min_R = 256
            _min_G = 256
            _min_B = 256
            pixels = self.imagen.load()
            #se itera en y
            for y in range(0,self.imagen.size[1]):
                if _min_R > self.imagen.getpixel((x,y))[0]:
                    _min_R = self.imagen.getpixel((x,y))[0]
                if _min_R > self.imagen.getpixel((x,y))[1]:
                    _min_R = self.imagen.getpixel((x,y))[1]
                if _min_R > self.imagen.getpixel((x,y))[2]:
                    _min_R = self.imagen.getpixel((x,y))[2]
            # Se resta el minimo
            for y in range(0, self.imagen.size[1]):
                pixels[x,y] = (pixels[x,y][0] - _min_R, pixels[x,y][1] - _min_G, pixels[x,y][2] - _min_B)
        self.imagen.save('mascara.jpg')
        plt.imshow(self.imagen.rotate(-90))
        plt.title('IMAGEN CON RESTA DEL MINIMO DE LA FILA POR PIXEL')
        plt.show()

    def imagen_binaria(self):
        '''Obtenemos una imagen binaria'''
        #Se abre la imagen en grayscale
        imagen = Image.open('mascara.jpg').convert("L")
        #Se transforma a matriz
        imagen = ndimage.rotate(imagen, -90)
        #Sefinimos un threshhold de 50, puesto que funciona bastante bien en todas las imagenes.
        imagen = np.asarray(imagen>50)
        plt.imshow(imagen, cmap='Greys_r')
        plt.title("IMAGEN BINARIA CON 'MANCHAS'")
        plt.show()
        #Se rellenan los 'hoyos' existentes
        imagen = ndimage.binary_fill_holes(imagen)
        #Se rellenan las manchas negras
        imagen = ndimage.binary_opening(imagen, structure=np.ones((5,5)).astype(int))
        #Se rellenan las manchas blancas
        imagen = ndimage.binary_closing(imagen, structure=np.ones((5,5)).astype(int))
        self.imagen_b = imagen
        #Se guarda la imagen obtenida
        scipy.misc.imsave('mascara.png',self.imagen_b)
        plt.imshow(self.imagen_b, cmap='Greys_r')
        plt.title('IMAGEN BINARIA SEGMENTADA')
        plt.show()
        os.remove('./mascara.jpg')