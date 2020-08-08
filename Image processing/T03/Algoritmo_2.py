import cv2
from matplotlib import pyplot as plt


class Algoritmo_2:

    def __init__(self, filename):
        '''Se lee la imagen y se reordenan los valores de los pixeles de la imagen para evitar problemas
        al graficarla, puesto que una vez abierta una imagen con el metodo cv2.imread() los valores de
        cada pixel estan ordenados de la siguiente forma: blue, green, red'''
        self.bgr_img = cv2.imread('./FOTOS_ALGORITMO_2/{}'.format(filename))
        # Se obtienen los valores
        self.b,self.g,self.r = cv2.split(self.bgr_img)
        # Se reordenan los valores
        self.rgb_img = cv2.merge([self.r,self.g,self.b])

    def run(self):
        ''' Se realizan todas las acciones necesarias para obtener la imagen deseada y luego graficarla '''
        # Se realiza un filtro de mediana de tamano 7
        self.rgb_img = cv2.medianBlur(self.rgb_img,7)
        # Se obtiene una imagen canny con los bordes de la imagen original
        self.canny = self.auto_canny(self.rgb_img)
        self.cambiar_colores()
        plt.imshow(self.rgb_img)
        plt.show()

    def auto_canny(self, image):
        # Metodo utilizado para obtener la imagen canny con los bordes de la imagen original
        edged = cv2.Canny(image, 0, 10)
        return edged

    def cambiar_colores(self):
        #Loop que recorre toda la imagen
        for x in range(self.rgb_img.shape[1]):
            for y in range(self.rgb_img.shape[0]):
                # Valores RBG del pixel
                r, g, b = self.rgb_img[y, x]
                # Si el pixel es blanco en la imagen canny y no casi negro en la imagen original
                if self.canny[y,x] == 255 and self.rgb_img[y,x][0]> 10 and self.rgb_img[y,x][1]> 10 and self.rgb_img[y,x][2]> 10:
                    try:
                        # A todos los pixeles seleccionados se les resta 1 en cada valor
                        # Si el valor es menor que 10, el valor sera 10.
                        self.rgb_img[y, x]= [max(r-1, 10),max(g-1, 10), max(b-1, 10)]
                        self.rgb_img[y, x+1]= [max(r-1, 10),max(g-1, 10), max(b-1, 10)]
                        self.rgb_img[y, x-1]= [max(r-1, 10),max(g-1, 10), max(b-1, 10)]
                        self.rgb_img[y+1, x]= [max(r-1, 10),max(g-1, 10), max(b-1, 10)]
                        self.rgb_img[y-1, x]= [max(r-1, 10),max(g-1, 10), max(b-1, 10)]
                        self.rgb_img[y+1, x-1]= [max(r-1, 10),max(g-1, 10), max(b-1, 10)]
                        self.rgb_img[y-1, x+1]= [max(r-1, 10),max(g-1, 10), max(b-1, 10)]
                        self.rgb_img[y-1, x-1]= [max(r-1, 10),max(g-1, 10), max(b-1, 10)]
                        self.rgb_img[y+1, x+1]= [max(r-1, 10),max(g-1, 10), max(b-1, 10)]
                    #Excepcion para los bordes
                    except:
                        pass

A = Algoritmo_2('12487273925_9a5bc6cf58_z.jpg')
A.run()