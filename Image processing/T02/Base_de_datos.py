
""" Clase creada con el objetivo de importar los datos de los cuadrantes de
las fallas, para que posteriormente sean graficados en la imagen original"""
class Base_de_datos:

    def __init__(self, filename):
        self.filename = filename
        self.fallas = []

    def añadir_fallas(self):
        with open(self.filename) as file:
            for line in file:
                line = line.replace('\n', '')
                line = line.split('   ')
                del line[0]
                line = [int(float(x)) for x in line]
                self.fallas.append(Falla(line))

class Falla:

    def __init__(self, *args):
        args = args[0]
        self.numero_imagen = args[0]
        self.x1 = args[1]
        self.y1 = args[2]
        self.x2 = args[3]
        self.y2 = args[4]