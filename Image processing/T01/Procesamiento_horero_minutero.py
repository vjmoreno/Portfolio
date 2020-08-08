import numpy as np
import os
from Funciones_importantes import barrido_polar, diferencia_angulos
from skimage import filters
from PIL import ImageEnhance
from scipy import ndimage, misc
from PIL import Image
from matplotlib import pyplot as plt

class Procesamiento_horero_minutero:

    def __init__(self, filename):
        self.filename = filename
        self.imagen = Image.open(self.filename).rotate(-90).convert('L')
        self.imagen_binaria = Image.open('mascara.png').convert('L')
        self.horero = None
        self.minutero = None
        self.lista_rectas = []

    def realizar_procesamiento(self):
        self.segmentar_reloj()
        self.centro_masa()
        self.lista_rectas = barrido_polar(self.centro, self.imagen)
        os.remove('./imagen_segmentada.png')

    def segmentar_reloj(self):
        '''Se procesa la imagen para que quede totalmente
        lista para luego buscarlas manecillas sin ningun problema'''
        #se carga la info de los pixeles de la imagen binaria previamente obtenida
        data_binario = self.imagen_binaria.load()
        # Se carga la info de los pixeles de la imagen original
        data = self.imagen.load()
        #Se recorre la imagen completa
        for x in range(0,self.imagen_binaria.size[0]):
            for y in range(0,self.imagen_binaria.size[1]):
                # Si el pixel no esta dentro de la region segmentada, el pixel se transforma a negro
                if data_binario[x,y] == 0:
                    data[x,y] = 0
        plt.imshow(self.imagen, cmap='Greys_r')
        plt.title('RELOJ SEGMENTADO')
        plt.show()
        #Aumentamos el contraste de la imagen
        contr = ImageEnhance.Contrast(self.imagen)
        im = contr.enhance(1.5)
        self.imagen = im
        #Transformamos la imagen a matriz
        imagen = ndimage.rotate(self.imagen, 0)
        #Aplicamos otsu
        val = filters.threshold_otsu(imagen)
        arr = np.asarray(imagen>val)
        #Tranformamos la imagen en escala de grises a una imagen binaria
        self.imagen = ndimage.binary_opening(arr)
        #Se guarda la imagen binaria segmentada
        misc.imsave('imagen_segmentada.png',self.imagen)
        #Se carga la imagen
        self.imagen = Image.open('imagen_segmentada.png').convert('L')
        plt.imshow(self.imagen, cmap='Greys_r')
        plt.title('RELOJ BINARIO SEGMENTADO')
        plt.show()


    def centro_masa(self):
        '''Metodo que busca el centro de masa
         de la 'mascara' (region segmentada)'''
        c = ndimage.measurements.center_of_mass(ndimage.rotate(self.imagen_binaria,0))
        self.centro = (int(c[1]), int(c[0]))

    def buscar_minutero(self):
        'Busca la manecilla correspondiente al minutero'
        max_ceros = 0
        #Itera sobre todas las rectas para encontrar la recta con mayor cantidad de ceros
        for recta in self.lista_rectas:
            ceros = recta.contar_ceros()
            if ceros > max_ceros:
                max_ceros = ceros
                self.minutero = recta
        plt.imshow(self.imagen, cmap='Greys_r')
        plt.scatter(self.centro[0], self.centro[1], c='red')
        plt.scatter(self.minutero.x2, self.minutero.y2, c='red')
        plt.scatter(self.minutero.centro[0], self.minutero.centro[1])
        plt.title('RESULTADO BUSQUEDA MINUTERO')
        plt.show()
        #Retorna el angulo del minutero
        return self.minutero.theta

    def buscar_horero(self):
        '''Busca la manecilla correspondiente al horero. Se debe
         buscar primeroel minutero para buscar el horero'''
        max_ceros = 0
        #Se itera sobre todas las rectas
        for recta in self.lista_rectas:
            ceros = recta.contar_ceros()
            #Si la recta tiene mas ceros que la anteriormente seleccionada, está ubicada a mas de 8 pixeles de
            #distancia del minutero en el eje x e y, y ademas tiene una diferencia de angulo de mas de 5 grados
            #con respecto al minutero
            if ceros > max_ceros and abs(recta.x2 - self.minutero.x2)>8 and abs(recta.y2 - self.minutero.y2)>8 and diferencia_angulos(self.minutero.theta, recta.theta)>5 :
                max_ceros = ceros
                self.horero = recta
        plt.imshow(self.imagen, cmap='Greys_r')
        plt.scatter(self.centro[0], self.centro[1], c='red')
        plt.scatter(self.horero.x2, self.horero.y2, c='red')
        plt.scatter(self.horero.centro[0], self.horero.centro[1])
        plt.title('RESULTADO BUSQUEDA HORERO')
        plt.show()
        return self.horero.theta