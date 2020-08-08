from Procesamiento_imagen import Procesamiento_imagen

def main():
    #rango de  imagenes que se quieren visualizar
    for x in range(52,55):
        if 1 <= x < 6:
            P = Procesamiento_imagen('./C0002/C0002_000{}.PNG'.format(x),150, 160, 3, 6, 10, x)
        elif 6 <= x < 10:
            P = Procesamiento_imagen('./C0002/C0002_000{}.PNG'.format(x), 115, 122, 4, 8, 15, x)
        elif x == 10:
            P = Procesamiento_imagen('./C0002/C0002_00{}.PNG'.format(x), 115, 122, 4, 8, 15, x)
        elif 11 <= x <20:
            P = Procesamiento_imagen('./C0002/C0002_00{}.PNG'.format(x), 170, 178, 3, 8, 5, x)
        elif 20 <= x < 29:
            P = Procesamiento_imagen('./C0002/C0002_00{}.PNG'.format(x), 107, 112, 4, 8, 50, x)
        elif 29 <= x < 37:
            P = Procesamiento_imagen('./C0002/C0002_00{}.PNG'.format(x), 210, 225, 3, 6, 5, x)
        elif 37 <= x < 47:
            #primera falla
            P = Procesamiento_imagen('./C0002/C0002_00{}.PNG'.format(x), 115, 122, 4, 8, 15, x)
            #segunda falla
            #P = Procesamiento_imagen('./C0002/C0002_00{}.PNG'.format(x), 100, 105, 1, 8, 50, x)
        elif 47 <= x < 53:
            P = Procesamiento_imagen('./C0002/C0002_00{}.PNG'.format(x), 210, 225, 3, 6, 5, x)
        elif 53 <= x < 60:
            P = Procesamiento_imagen('./C0002/C0002_00{}.PNG'.format(x), 140, 150, 4, 8, 15, x)

        P.restar_imagenes()
        P.filtrado()
        P.plot_fourier()
        P.fourier_inversa()
        P.binario()
        P.barrido_x()
        P.barrido_y()
        P.encontrar_regiones()
        P.filtrar_posiciones()
        P.plot_fallas()

main()