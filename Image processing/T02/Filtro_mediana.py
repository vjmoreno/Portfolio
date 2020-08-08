from PIL import Image
from matplotlib import pyplot as plt
from statistics import median

class Filtro_mediana:

    def __init__(self, filename):
        self.filename = filename
        self.imagen = Image.open(self.filename)
        self.m = Mediana(1, 5, 0, -5)

    def filtro_mediana(self):
        data = self.imagen.load()
        for x in range(self.imagen.size[0]):
            for y in range(self.imagen.size[1]):
                try:
                    data[x,y] = median([data[x + self.m.x1,y + self.m.x1], data[x + self.m.x2,y + self.m.x2], data[x + self.m.x3,y + self.m.x3]])
                except:
                    pass

        plt.imshow(self.imagen, cmap='Greys_r')
        plt.show()


class Mediana:

    def __init__(self, tamaño, x1, x2, x3):
        self.tamaño = tamaño
        self.x1 = x1
        self.x2 = x2
        self.x3 = x3

M = Filtro_mediana('./C0002/C0002_0002.PNG')
M.filtro_mediana()