from PIL import Image
from matplotlib import pyplot as plt
import numpy as np
from scipy import ndimage, misc
from Base_de_datos import Base_de_datos, Falla

class Procesamiento_imagen:

    def __init__(self, filename, color_min, color_max, tamaño_min, tamaño_max, tamaño_mediana, nro_imagen):
        self.filename = filename
        # color minimo de la falla (numero entre 0 y 255)
        self.color_min = color_min
        #color maximo de la falla
        self.color_max =color_max
        # tamaño minimo de la falla
        self.tamaño_min = tamaño_min
        #tamaño maximo de la falla
        self.tamaño_max = tamaño_max
        # tamaño del filtro de mediana
        self.tamaño_mediana = tamaño_mediana
        self.numero_imagen = nro_imagen
        self.base_datos = Base_de_datos('./C0002/ground_truth.txt')
        # se importan los datos de los cuadrantes de las fallas
        self.base_datos.añadir_fallas()
        self.imagen = Image.open(self.filename).convert('L')
        self.imagen_inicial = Image.open(self.filename).convert('L')
        self.imagen2 = ndimage.rotate(self.imagen, 0)
        #imagen que se le aplica un filtro de mediana
        self.imagen2 = ndimage.median_filter(self.imagen, self.tamaño_mediana)
        self.imagen2 = Image.fromarray(self.imagen2)
        #se le aplica fourier a la imagen con filtro de mediana
        self.imagen_fourier = np.fft.fftshift(np.fft.fft2(self.imagen2))
        self.radio = 8
        self.lista_x = []
        self.lista_y = []
        self.posiciones_x = []
        self.posiciones_y = []
        self.posiciones_posibles = []

    def plot_fourier(self):
        #graficar transformada de fourier 2d
        plt.imshow(np.log(Image.fromarray(abs(self.imagen_fourier))), cmap='Greys_r') #siempre graficaremos el log de la transformada
        plt.title("|F(k)|")
        plt.show()

    def restar_imagenes(self):
        #a la imagen inicial se le resta la imagen con filtro de mediana y posteriormente se grafica
        data1 = self.imagen.load()
        data2 = self.imagen2.load()
        for x in range(self.imagen.size[0]):
            for y in range(self.imagen.size[1]):
                data1[x,y] = data1[x,y] - data2[x,y]
        self.imagen_fourier = np.fft.fftshift(np.fft.fft2(self.imagen))
        plt.subplot(211)
        plt.title('IMAGEN ORIGINAL - IMAGEN FILTRO MEDIANA')
        plt.imshow(self.imagen, cmap='Greys_r')
        plt.subplot(212)
        plt.title('IMAGEN ORIGINAL')
        plt.imshow(self.imagen_inicial, cmap='Greys_r')
        plt.show()


    def filtrado(self):
        # se aplica un filtro pasa banda conformado por dos filtros butterworth
        centro = (int(len(self.imagen_fourier)/2), int(len(self.imagen_fourier[0])/2))
        for x in range(len(self.imagen_fourier)):
            for y in range(len(self.imagen_fourier[0])):
                self.imagen_fourier[x,y] = self.imagen_fourier[x, y]*self.filtro_butterworth(centro[0], centro[1], x, y) + 0.01


    def filtro_butterworth (self, x0, y0, x1, y1):
        #frecuencias de corte los filtros
        frec_corte1 = 30
        frec_corte2 = 10
        # parametro n de la formula
        n1 = 4
        n2 = 2
        funcion1 = 1/(1+(self.distancia_dos_puntos(x0, y0, x1, y1)/frec_corte1)**(2*n1))
        funcion2 = 1/(1+(self.distancia_dos_puntos(x0, y0, x1, y1)/frec_corte2)**(2*n2))
        # se restan los filtros para crear el filtro pasa banda
        return funcion1- funcion2

    def distancia_dos_puntos(self, x0, y0, x1, y1):
        #funcion que me entrega la distancia entre dos pixeles
        return ((x0-x1)**2 +(y0-y1)**2)**0.5

    def fourier_inversa(self):
        #se calcula la transformada inversa de fourier de la imagen procesada con el filtro pasabanda
        f_ishift = np.fft.ifftshift(self.imagen_fourier)
        img_back = np.fft.ifft2(f_ishift)
        self.imagen_filtrada = abs(img_back)
        misc.imsave('imagen_filtrada.png', self.imagen_filtrada)
        # se grafica la imagen filtrada
        plt.imshow(self.imagen_filtrada, cmap='Greys_r')
        plt.title('IMAGEN CON FILTRO PASA BANDA BUTTERWORTH')
        plt.show()


    def barrido_x(self):
        """funcion que realiza un barrido en el eje x de la imagen binaria
        con el objetivo de buscar lineas blancas horizontales de un determinado tamaño"""
        data = self.imagen_filtrada.load()
        self.lista_x =[]
        self.posiciones_x = []
        for y in range(self.imagen_filtrada.size[1]):
            contador = 0
            for x in range(self.imagen_filtrada.size[0]):
                if data[x, y] == 255:
                    contador += 1
                    self.posiciones_x.append((x,y))
                elif data[x, y] == 0:
                    if self.tamaño_min < contador < self.tamaño_max:
                        self.lista_x.append(self.posiciones_x)
                    self.posiciones_x = []
                    contador = 0

    def barrido_y(self):
        """funcion que realiza un barrido en el eje y de la imagen binaria
        con el objetivo de buscar lineas blancas verticales de un determinado tamaño"""
        data = self.imagen_filtrada.load()
        self.lista_y =[]
        self.posiciones_y = []
        for x in range(self.imagen_filtrada.size[0]):
            contador = 0
            for y in range(self.imagen_filtrada.size[1]):
                if data[x, y] == 255:
                    contador += 1
                    self.posiciones_y.append((x,y))
                elif data[x, y] == 0:
                    if self.tamaño_min < contador < self.tamaño_max:
                        self.lista_y.append(self.posiciones_y)
                    self.posiciones_y = []
                    contador = 0

    def encontrar_regiones(self):
        """funcion que busca la interseccion de las lineas blancas verticales con la horizontales de
        llos metodos barrido_x y barrido_y, con el objetivo de encontrar 'islas' blancas de un
        determinado tamaño"""
        data = self.imagen_inicial.load()
        self.posiciones_posibles = []
        self.posiciones_finales = []
        for lista_posiciones in self.lista_x:
            for posicion in lista_posiciones:
                for lista_posiciones in self.lista_y:
                    if posicion in lista_posiciones:
                      if lista_posiciones not in self.posiciones_posibles:
                          self.posiciones_posibles.append(lista_posiciones)
        plt.imshow(self.imagen_filtrada, cmap='Greys_r')
        for lista_posiciones in self.posiciones_posibles:
            for posicion in lista_posiciones:
                if self.color_min < data[posicion[0], posicion[1]] < self.color_max:
                    self.posiciones_finales.append(posicion)
                    plt.scatter(posicion[0], posicion[1], c='red')
        plt.title('IMAGEN CON POSIBLES FALLAS (ROJO)')
        plt.show()

    def filtrar_posiciones(self):
        "filtra las islas segun la distancia de los puntos"
        final = []
        for posicion in self.posiciones_finales:
            for posicion2 in self.posiciones_finales:
                if posicion != posicion2:
                    if self.distancia_dos_puntos(posicion[0], posicion[1], posicion2[0], posicion2[1]) < 2:
                        final.append(posicion)
                        final.append(posicion2)
        #posiciones finales luego del filtrado de posiciones de los puntos
        self.posiciones_finales = final

    def plot_fallas(self):
        """Grafica la imagen con las posibles fallas a traves de puntos rojos y tambien
        grafica las esquinas de los cuadrantes en los cuales existen fallas (puntos azules)"""
        for f in self.base_datos.fallas:
            if f.numero_imagen == self.numero_imagen:
                falla = f
                imagen = Image.open(self.filename)
                imagen2 = Image.open(self.filename)
                data = imagen.load()
                x1 = min(falla.x1, falla.y1)
                x2 = max(falla.x1, falla.y1)
                y1 = min(falla.y2, falla.x2)
                y2 = max(falla.y2, falla.x2)
                puntos = [(x1, y1), (x2, y1),(x2, y2), (x1, y2)]
                plt.imshow(self.imagen_inicial, cmap='Greys_r')
                for punto in puntos:
                    plt.scatter(punto[0], punto[1], c= 'blue')
                for posicion in self.posiciones_finales:
                    plt.scatter(posicion[0], posicion[1], c='red')
                plt.title('IMAGEN CON FALLAS FINALES Y CUADRANTE DE FALLA REAL')
                plt.show()


    def binario(self):
        """Construye una imagen binaria con las posibles fallas segmentadas
         y la grafica"""
        self.imagen_filtrada = Image.fromarray(self.imagen_filtrada)
        data = self.imagen_filtrada.load()
        for x in range(self.imagen_filtrada.size[0]):
            for y in range(self.imagen_filtrada.size[1]):
                if 1 < data[x,y] < 10:
                    data[x,y] = 255
                else:
                    data[x,y] = 0
        plt.imshow(self.imagen_filtrada, cmap='Greys_r')
        plt.title('IMAGEN BINARIA CON POSIBLES FALLAS SEGMENTADAS')
        plt.show()
        misc.imsave('imagen_binaria.png',self.imagen_filtrada)

