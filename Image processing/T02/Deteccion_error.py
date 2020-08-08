from Deteccion_de_circulos import Deteccion_de_circulos
from PIL import Image
from matplotlib import pyplot as plt
from skimage import color
import scipy

matriz_4 = [[0, 0, 0, 0, 0, 0],
            [0, 0, 1, 1, 0, 0],
            [0, 1, 1, 1, 1, 0],
            [0, 1, 1, 1, 1, 0],
            [0, 0, 1, 1, 0, 0],
            [0, 0, 0, 0, 0, 0]]

matriz_5 = [[0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 1, 0, 0, 0],
            [0, 0, 1, 1, 1, 0, 0],
            [0, 1, 1, 1, 1, 1, 0],
            [0, 0, 1, 1, 1, 0, 0],
            [0, 0, 0, 1, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0]]

matriz_6 = [[0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 1, 1, 0, 0, 0],
            [0, 0, 1, 1, 1, 1, 0, 0],
            [0, 1, 1, 1, 1, 1, 1, 0],
            [0, 1, 1, 1, 1, 1, 1, 0],
            [0, 0, 1, 1, 1, 1, 0, 0],
            [0, 0, 0, 1, 1, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0]]

matriz_7 = [[0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 1, 0, 0, 0, 0],
            [0, 0, 0, 1, 1, 1, 0, 0, 0],
            [0, 0, 1, 1, 1, 1, 1, 0, 0],
            [0, 1, 1, 1, 1, 1, 1, 1, 0],
            [0, 0, 1, 1, 1, 1, 1, 0, 0],
            [0, 0, 0, 1, 1, 1, 0, 0, 0],
            [0, 0, 0, 0, 1, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0]]

matriz_8 = [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 1, 1, 0, 0, 0, 0],
            [0, 0, 0, 1, 1, 1, 1, 0, 0, 0],
            [0, 0, 1, 1, 1, 1, 1, 1, 0, 0],
            [0, 1, 1, 1, 1, 1, 1, 1, 1, 0],
            [0, 1, 1, 1, 1, 1, 1, 1, 1, 0],
            [0, 0, 1, 1, 1, 1, 1, 1, 0, 0],
            [0, 0, 0, 1, 1, 1, 1, 0, 0, 0],
            [0, 0, 0, 0, 1, 1, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]

class Deteccion_error:

    def __init__(self, centros, filename):
        self.centros = centros
        self.circulos = [Circulo(centro) for centro in self.centros]
        self.filename = filename
        self.imagen = Image.open(filename)
        self.matriz_4 = matriz_4
        self.matriz_5 = matriz_5
        self.matriz_6 = matriz_6
        self.matriz_7 = matriz_7
        self.matriz_8 = matriz_8
        matriz = self.matriz_5
        centro = [len(matriz[0])//2, len(matriz[0])//2]
        print(list(range(centro[0],-centro[0] -1,-1)))

    def errores(self):
        data = self.imagen.load()
        matrices = [self.matriz_4, self.matriz_5, self.matriz_6, self.matriz_7, self.matriz_8]
        min_errores = float('inf')
        min_centro = None
        min_radio = None
        for centro in self.centros:
            for matriz in matrices:
                errores = 0
                if len(matriz[0]) % 2 == 0:
                    c = [len(matriz[0])//2, len(matriz[0])//2]
                    for x in range(c[0],-c[0],-1):
                        for y in range(c[0],-c[0],-1):
                            try:
                                if (data[int(centro[1]) + x, int(centro[0]) + y] == 255 and matriz[x][y] == 0) or (data[int(centro[1]) + x, int(centro[0]) + y] == 0 and matriz[x][y] == 1):
                                    errores += 1
                            except:
                                pass
                else:
                    c = [len(matriz[0])//2 + 1, len(matriz[0])//2 + 1]
                    for x in range(centro[0],-centro[0] -1,-1):
                        for y in range(centro[0],-centro[0] -1,-1):
                            try:
                                if (data[int(centro[1]) + x,int(centro[0]) + y] == 255 and matriz[x][y] == 0) or (data[int(centro[1]) + x, int(centro[0]) + y] == 0 and matriz[x][y] == 1):
                                    errores += 1
                            except:
                                pass
                if errores < min_errores:
                    min_errores = errores
                    min_centro = centro
                    min_radio = len(matriz)-2
        print(min_errores, min_centro, min_radio)
        imagen = scipy.misc.imread(self.filename)
        imagen = color.gray2rgb(imagen)
        imagen[min_centro[0], min_centro[1]] = (220, 20, 20)
        plt.imshow(imagen, cmap=plt.cm.gray)
        plt.show()


class Circulo:

    def __init__(self, centro):
        self.centro = centro
        self.errores = 0

D = Deteccion_de_circulos('./imagen_binaria.png')
D.encontrar_circulos()
centros = D.centros
D2 = Deteccion_error(centros,'./imagen_binaria.png')
D2.errores()