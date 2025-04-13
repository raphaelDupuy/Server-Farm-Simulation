import heapq
from enum import Enum
    
class Evenement(Enum):

    NR = 0 # nouvelle requête
    RAR = 1 # requête à router
    FT = 2 # fin traitement


class Echeancier:
    def __init__(self):
        self.echeancier = []
        self.temps_actuel = 0.0

    def __str__(self):
        res = ""
        for event in self.echeancier:
            res += f"{event[0]} : {event[1]} - {event[2]}\n"
        return res

    def ajouter_evenement(self, temps : float, type_evenement : Evenement, details):
        heapq.heappush(self.echeancier, (temps, type_evenement, details))
    
    def prochain_evenement(self):
        if self.echeancier:
            self.temps_actuel, type_evenement, details = heapq.heappop(self.echeancier)
            return type_evenement, details
        else:
            return None, None
    
    def est_vide(self):
        return len(self.echeancier) == 0

