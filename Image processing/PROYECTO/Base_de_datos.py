

class Base_de_datos:

    def __init__(self, filename):
        self.filename = filename
        self.fallas = {}

    def anadir_fallas(self):
        with open(self.filename, 'r') as file:
            ok = False
            for line in file:
                if not ok:
                    ok = True
                else:
                    line = line.replace('\n', '')
                    line = line.split('\t')
                    line =  [0 if x=='' else x for x in line]
                    falla = Falla(line)
                    self.fallas[falla.filename] = falla

        return self.fallas

class Falla:

    def __init__(self, *args):
        args = args[0]
        self.filename = args[0]
        self.x = int(args[4])
        self.y = int(args[5])
        self.r = int(args[6])

B = Base_de_datos('./groundtruth.txt')
B.anadir_fallas()