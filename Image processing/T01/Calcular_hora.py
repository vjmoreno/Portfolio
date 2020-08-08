from math import pi

class Calcular_hora:

    def __init__(self, angulo_horero, angulo_minutero, angulo_segundero):
        self.angulo_horero = angulo_horero
        self.angulo_minutero = angulo_minutero
        self.angulo_segundero = angulo_segundero

    def redefinir_agulos(self, angulo):
        '''Metodo creado debido a que el los sistemas
        de angulos de la hora y de las rectas no calzan'''
        if  0  <= angulo <= 270:
            angulo = 90 + angulo
        else:
            angulo = angulo -270
        return angulo

    def calcular_hora(self):
        'Metodo que calcula la hora'
        #se transforman los radianes a grados hexagesimales
        a_hora = self.redefinir_agulos(self.angulo_horero*360/(2*pi))
        a_minuto = self.redefinir_agulos(self.angulo_minutero*360/(2*pi))
        a_segundo = self.redefinir_agulos(self.angulo_segundero*360/(2*pi))
        #se calcula la hora
        horas = int(a_hora/30)
        minutos = int(a_minuto/6)
        segundos = int(a_segundo/6)
        if minutos < 10:
            minutos = '0'+str(minutos)
        if segundos < 10:
            segundos = '0'+str(segundos)
        #se imprime por consola
        print('[HORA]: {}:{}:{}'.format(horas, minutos, segundos))









