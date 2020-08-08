

class Recta:
    ''' Clase que defina a todas las rectas que
    potencialmente pueden ser horeros, minuteros o segunderos'''
    def __init__(self, centro, lista, theta, x2, y2):
        self.centro = centro
        self.lista = lista
        self.theta = theta
        self.x2 = x2
        self.y2 = y2

    def contar_ceros(self):
        cont = 0
        for elemento in self.lista:
            if elemento == 0:
                cont+=1
        return cont