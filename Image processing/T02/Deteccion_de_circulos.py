import numpy as np
import matplotlib.pyplot as plt
import scipy
from skimage import color
from skimage.transform import hough_circle
from skimage.feature import peak_local_max, canny
from skimage.draw import circle_perimeter


class Deteccion_de_circulos:

    def __init__(self, filename):
        self.filename = filename
        self.imagen = scipy.misc.imread(self.filename)
        self.bordes = canny(self.imagen, sigma=3, low_threshold=10, high_threshold=70)
        self.hough_radios = np.arange(2, 8, 1)
        self.hough_res = hough_circle(self.bordes, self.hough_radios)
        self.centros = []
        self.accumulaciones = []
        self.radios = []

    def encontrar_circulos(self):
        for radio, h in zip(self.hough_radios, self.hough_res):
            num_peaks = 2 #dos circulos por radio
            peaks = peak_local_max(h, num_peaks=num_peaks)
            self.centros.extend(peaks)
            self.accumulaciones.extend(h[peaks[:, 0], peaks[:, 1]])
            self.radios.extend([radio] * num_peaks)

    def dibujar_circulos(self):
        self.imagen = color.gray2rgb(self.imagen)
        for idx in np.argsort(self.accumulaciones):
            center_x, center_y = self.centros[idx]
            radio = self.radios[idx]
            cx, cy = circle_perimeter(center_y, center_x, radio)
            self.imagen[cy, cx] = (220, 20, 20)
        plt.imshow(self.imagen, cmap=plt.cm.gray)
        plt.show()


D = Deteccion_de_circulos('./imagen_binaria.png')
D.encontrar_circulos()
D.dibujar_circulos()