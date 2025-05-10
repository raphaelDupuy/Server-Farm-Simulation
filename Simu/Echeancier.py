import heapq
from enum import Enum


class Ev(Enum):
    NR = 0    # Nouvelle requête
    RAR = 1   # Requête à router
    FT = 2    # Fin de traitement

class Echeancier:
    def __init__(self):
        self.echeancier = []
        self.temps_actuel = 0.0
        self.historique = []  # tuples (temps, id, detail)

        # pour l'intégrale du nb moyen de requêtes dans le systeme
        self.sum_L = 0.0
        self.last_time = 0.0
        self.last_L = 0

    def ajouter_historique(self, temps, id, detail):
        self.historique.append((temps, id, detail))

    def ajouter_evenement(self, temps: float, type_evenement: Ev, details):
        heapq.heappush(self.echeancier, (temps, type_evenement, details))

    def prochain_evenement(self):
        if self.echeancier:
            self.temps_actuel, type_evenement, details = heapq.heappop(self.echeancier)
            return type_evenement, details
        return None, None

    def est_vide(self):
        return not self.echeancier
    
    # mettre à jour le nb de requêtes pondéré dans le systeme
    def update_L(self, current_L):
        dt = self.temps_actuel - self.last_time
        self.sum_L += self.last_L * dt
        self.last_time = self.temps_actuel
        self.last_L = current_L
    
    # moyenne de l'intégrale
    def moyenne_L(self):
        return self.sum_L / self.temps_actuel if self.temps_actuel > 0 else 0