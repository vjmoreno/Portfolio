from PIL import Image
from matplotlib import pyplot as plt
from Base_de_datos import Base_de_datos, Falla
from main import *
import numpy as np

class Diferencias:
    def __init__(self):
        self.base_datos = Base_de_datos('./C0002/ground_truth.txt')
        self.base_datos.añadir_fallas()

    def plot_cambios_fourier(self):
        for falla in self.base_datos.fallas:
            if falla.numero_imagen < 10:
                filename = './C0002/C0002_000{}.png'.format(falla.numero_imagen)
            else:
                filename = './C0002/C0002_00{}.png'.format(falla.numero_imagen)
            imagen = Image.open(filename)
            imagen2 = Image.open(filename)
            data = imagen.load()
            x1 = min(falla.x1, falla.y1)
            x2 = max(falla.x1, falla.y1)
            y1 = min(falla.y2, falla.x2)
            y2 = max(falla.y2, falla.x2)
            for x in range(x1, x2):
                for y in range(y1, y2):
                    data[x, y] = 0
            f1 = np.fft.fftshift(np.fft.fft2(imagen))
            f2 = np.fft.fftshift(np.fft.fft2(imagen2))
            plt.subplot(211)
            plt.imshow(np.log(Image.fromarray(abs(f2))), cmap='Greys_r')
            plt.subplot(212)
            plt.imshow(np.log(Image.fromarray(abs(f1))), cmap='Greys_r')
            plt.show()
