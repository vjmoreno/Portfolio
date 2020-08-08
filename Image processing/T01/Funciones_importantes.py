from math import sin, cos, pi
from Recta import Recta


def barrido_polar(centro, imagen):
    '''Funcion que realiza un barrido en coordenadas polares
    para armar las diferentes ecuaciones de recta. La recta es
    armada a partir de dos puntos, el centro y un punto ubicado
    a 60 pixeles de distancias. El angulo theta varia de 0 a 2*pi
    y el centro va siendo ubicado en diferentes posiciones, debido
    a que existen pequeños errores en el calculo del centro de
    masa y además la umagen binaria sobre la cual se trabaja no es
    totalmente perfecta'''
    lista_rectas = []
    p = 60
    #variacion en x del centro
    for _x in range(-6, 6):
        #variacion en y del centro
        for _y in range(-6, 6):
            #centro
            origen = (centro[0] + _x, centro[1] + _y)
            #variacion del angulo
            for angulo in range(360):
                theta = angulo*2*pi/360
                x = p*cos(theta)+origen[0]
                y = p*sin(theta)+origen[1]
                #armamos la ecuacion de la recta
                ecuacion_recta(origen[0], origen[1],x, y, theta, origen, imagen, lista_rectas)
    #se retorna una lista con todas las rectas encontradas
    return lista_rectas


def ecuacion_recta(x1,y1,x2,y2, theta, origen, imagen, lista_rectas):
    '''Funcion que arma las diferentes ecuaciones
     de recta a partir delangulo y el centro'''
    #cargamos la info de los pixeles
    data =imagen.load()
    lista = []
    #se itera 60 veces para conseguir la informacion de los colores de los pixeles de la recta
    for number in range(60):
        x = int(x1+ number*cos(theta))
        y = int(y1+ number*sin(theta))
        lista.append(data[x,y])
    #se agrega la recta a la lista
    lista_rectas.append(Recta(origen, lista, theta, x2, y2))

def diferencia_angulos(a1, a2):
    'Funcion que calcula la diferencia entre 2 angulos'
    a1 = a1*360/(2*pi)
    a2 = a2*360/(2*pi)
    dif_angulos = 180 - abs(abs(a1 - a2) - 180)
    return dif_angulos