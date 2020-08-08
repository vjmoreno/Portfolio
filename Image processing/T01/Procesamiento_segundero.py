import os
from Funciones_importantes import barrido_polar, diferencia_angulos
from matplotlib import pyplot as plt
from PIL import Image

class Procesamiento_segundero:

    def __init__(self, filename, angulo_horero, angulo_minutero, centro):
        self.centro = centro
        self.filename = filename
        self.angulo_horero = angulo_horero
        self.angulo_minutero = angulo_minutero
        self.lista_rectas = []
        self.imagen = Image.open(self.filename).rotate(-90).convert('L')
        self.imagen_binaria = Image.open('mascara.png').convert('L')

    def realizar_procesamiento(self):
        'Metodo que realiza todos los procesos'
        self.rango_gris_segundero()
        self.lista_rectas = barrido_polar(self.centro, self.imagen)
        self.buscar_segundero()
        #Se elimina la mascada (imagen segmentada)
        os.remove('./mascara.png')
        #Se retorna el angulo del segundero
        return self.segundero.theta

    def rango_gris_segundero(self):
        '''Lo que se intenta hacer con este metodo es que
         los pixeles que esten dentro de un rango de gris
        sean de color negro y los que no, sean de color
        blanco. Por loq eu se termina obteniendo una imagen
        binaria'''
        data_binario = self.imagen_binaria.load()
        data = self.imagen.load()
        #Se recorre la imagen
        for x in range(0,self.imagen_binaria.size[0]):
            for y in range(0,self.imagen_binaria.size[1]):
                #Se hace color blanco todo lo que esta fuera del reloj atraves de la mascara creada
                if data_binario[x,y] == 0:
                    data[x,y] = 255
                #Se hace negro todo lo que esta dentro del posible rango de gris del segundero
                elif 100 < data[x,y] < 200:
                    # se tranforman a negro todos los vecinos del pixel
                    data[x,y] = 0
                    data[x+1,y] = 0
                    data[x,y+1] = 0
                    data[x-1,y] = 0
                    data[x,y-1] = 0
                    data[x+1,y-1] = 0
                    data[x+1,y+1] = 0
                    data[x-1,y+1] = 0
                    data[x-1,y-1] = 0
                else:
                    data[x,y] = 255
        plt.imshow(self.imagen, cmap='Greys_r')
        plt.title('FILTRADO DE COLOR DEL SEGUNDERO')
        plt.show()

    def buscar_segundero(self):
        '''Busca el segundero casi de la misma forma
        en que fue buscado el horero y el minutero'''
        max_ceros = 0
        #Se itera sobre todas las rectas
        for recta in self.lista_rectas:
            ceros = recta.contar_ceros()
            # Si tiene mas ceros que la recta anterior y tien una diferencia de 10 grados tanto con el minutero como con el horero
            if ceros > max_ceros and abs(diferencia_angulos(self.angulo_horero, recta.theta))>10 and abs(diferencia_angulos(self.angulo_minutero, recta.theta))>10 :
                max_ceros = ceros
                self.segundero = recta
        plt.imshow(self.imagen, cmap='Greys_r')
        plt.scatter(self.centro[0], self.centro[1], c='red')
        plt.scatter(self.segundero.x2, self.segundero.y2, c='red')
        plt.scatter(self.segundero.centro[0], self.segundero.centro[1])
        plt.title('RESULTADO BUSQUEDA SEGUNDERO')
        plt.show()






