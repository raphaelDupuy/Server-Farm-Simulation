import random
from Echeancier import Echeancier, Ev

default_lambda_serv = 14/20
class Routeur:
    def __init__(self, nb_groupes: int, echeancier: Echeancier):
        if nb_groupes not in {1,2,3,6}:
            raise ValueError("Nombre de groupes incorrect")
        self.nb_groupes = nb_groupes
        self.echeancier = echeancier
        self.nb_attente = 0
        self.perte = 0
        self.nb_total = 0
        self.queue = []  # file FIFO pour requêtes en attente
        self.groupes = {}
        # délai de routage selon nombre de groupes
        self.temps_routage = {
            1: 0,
            2: 4/20,
            3: 7/20,
            6: 10/20
        }[nb_groupes]

    def add_groupes(self, groupes):
        # groupes: liste de listes, index correspond à spe
        self.groupes = {i: grp for i, grp in enumerate(groupes)}

    def ajoute_requete(self, requete):
        self.nb_total += 1
        t0 = self.echeancier.temps_actuel
        self.echeancier.ajouter_historique(t0, requete.get_id(), 0)
        if self.nb_attente < 100:
            # programmation du routage
            t_rar = t0 + random.expovariate(1/self.temps_routage) if self.temps_routage>0 else t0
            self.echeancier.ajouter_evenement(t_rar, Ev.RAR, requete)
            self.nb_attente += 1
        else:
            self.perte += 1

    def route_requete(self, requete):
        spe = requete.get_value()
        if spe not in self.groupes:
            raise KeyError(f"Spécialisation {spe} non définie dans groupes")
        # recherche d'un serveur libre
        for serveur in self.groupes[spe]:
            if not serveur.occupe:
                serveur.traite(requete)
                self.nb_attente -= 1
                return
        # mise en attente FIFO
        self.queue.append(requete)

    def notify(self, serveur_libere):
        # un serveur vient de se libérer, on tente de traiter la tête de file (FIFO)
        if self.queue:
            req = self.queue.pop(0)
            # réacheminement via route_requete pour respecter la spécialisation
            self.route_requete(req)