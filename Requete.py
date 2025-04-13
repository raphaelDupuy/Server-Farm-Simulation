from enum import Enum

class Requete:
    nb_instances = 0

    def __init__(self, spe=0):
        Requete.nb_instances += 1
        self.id = Requete.nb_instances
        self.spe = Requetes(spe)
class Requetes(Enum):
        
    SPE0 = 0
    SPE1 = 1
    SPE2 = 2
    SPE3 = 3
    SPE4 = 4
    SPE5 = 5