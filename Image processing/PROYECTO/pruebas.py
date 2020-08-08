from Base_de_datos import *
from PIL import Image, ImageFilter
import numpy as np
from scipy import misc
from matplotlib import pyplot as plt
from scipy import ndimage

class Filtro_mediana:

    def __init__(self, filename):
        B = Base_de_datos('./groundtruth.txt')
        self.fallas = B.anadir_fallas()
        self.filename = filename
        self.imagen2 = Image.open('./imagenes/'+ filename)
        #self.plot_imagen(self.imagen2)
        self.imagen_fourier = np.fft.fftshift(np.fft.fft2(self.imagen2))
        self.filtrado()
        self.fourier_inversa()
        self.binario()
        #self.plot_imagen(self.imagen_filtrada)

    def filtro_butterworth (self, x0, y0, x1, y1):
        #frecuencias de corte los filtros
        frec_corte1 = 20
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

    def filtrado(self):
        # se aplica un filtro pasa banda conformado por dos filtros butterworth
        centro = (int(len(self.imagen_fourier)/2), int(len(self.imagen_fourier[0])/2))
        for x in range(len(self.imagen_fourier)):
            for y in range(len(self.imagen_fourier[0])):
                self.imagen_fourier[x,y] = self.imagen_fourier[x, y]*self.filtro_butterworth(centro[0], centro[1], x, y) + 0.01

    def plot_fourier(self):
        #graficar transformada de fourier 2d
        plt.imshow(np.log(Image.fromarray(abs(self.imagen_fourier))), cmap='Greys_r') #siempre graficaremos el log de la transformada
        plt.title("|F(k)|")
        plt.show()

    def fourier_inversa(self):
        #se calcula la transformada inversa de fourier de la imagen procesada con el filtro pasabanda
        f_ishift = np.fft.ifftshift(self.imagen_fourier)
        img_back = np.fft.ifft2(f_ishift)
        self.imagen_filtrada = abs(img_back)
        self.imagen_filtrada = Image.fromarray(self.imagen_filtrada)

    def plot_imagen(self, imagen):
        falla = self.fallas[self.filename[0:-4]]
        c1 = plt.Circle((falla.x, 1024 - falla.y), falla.r, color=(1, 0, 0), fill=False)
        fig = plt.figure()
        plt.imshow(imagen, cmap='Greys_r')
        fig.add_subplot(111).add_artist(c1)
        plt.show()

    def binario(self):
        data = self.imagen_filtrada.load()
        data2 = self.imagen2.load()
        for x in range(self.imagen_filtrada.size[0]):
            for y in range(self.imagen_filtrada.size[1]):
                if data[x,y] > 5 and data2[x,y] > 155:
                    data[x,y] = 255
                else:
                    data[x,y] = 0
        self.imagen_filtrada = ndimage.binary_fill_holes(self.imagen_filtrada)
        #Se rellenan las manchas negras
        self.imagen_filtrada = ndimage.binary_opening(self.imagen_filtrada, structure=np.ones((10,10)).astype(int))
        #Se rellenan las manchas blancas
        self.imagen_filtrada = ndimage.binary_closing(self.imagen_filtrada, structure=np.ones((10,10)).astype(int))
        misc.imsave(self.filename+'.png',self.imagen_filtrada)

for x in range(1,10):
    Filtro_mediana('mdb00{}.png'.format(x))