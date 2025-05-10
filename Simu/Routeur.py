import random
from Echeancier import Echeancier, Ev

default_lambda_serv = 14/20

class Routeur:
    def __init__(self, nb_groupes: int, echeancier: Echeancier):
        if nb_groupes not in {1, 2, 3, 6}:
            raise ValueError("Nombre de groupes incorrect")
        self.nb_groupes = nb_groupes
        self.echeancier = echeancier
        self.nb_attente = 0
        self.perte = 0
        self.nb_total = 0
        self.queue = []  # file FIFO pour requêtes en attente
        self.groupes = {}

        # pour calcul de Little
        self.nb_occupe = 0  # Nombre de requêtes en traitement
        self.aire_L = 0.0
        self.t_precedent = 0.0

        # délai de routage selon nombre de groupes
        self.temps_routage = {
            1: 0,
            2: 4/20,
            3: 7/20,
            6: 10/20
        }[nb_groupes]

    def update_L(self):
        t = self.echeancier.temps_actuel
        dt = t - self.t_precedent
        self.aire_L += dt * self.nb_occupe
        self.t_precedent = t

    def add_groupes(self, groupes):
        # groupes: liste de listes, index correspond à spe
        self.groupes = {i: grp for i, grp in enumerate(groupes)}

    def ajoute_requete(self, requete):
        self.nb_total += 1
        t0 = self.echeancier.temps_actuel
        self.echeancier.ajouter_historique(t0, requete.get_id(), 0)
        if self.nb_attente < 100:
            # programmation du routage
            t_rar = t0 + random.expovariate(1 / self.temps_routage) if self.temps_routage > 0 else t0
            self.echeancier.ajouter_evenement(t_rar, Ev.RAR, requete)
            self.nb_attente += 1
        else:
            self.perte += 1

    def route_requete(self, requete):
        spe = requete.get_value()
        if spe not in self.groupes:
            raise KeyError(f"Spécialisation {spe} non définie dans groupes")
        for serveur in self.groupes[spe]:
            if not serveur.occupe:
                self.update_L()
                self.nb_occupe += 1
                self.echeancier.update_L(self.nb_occupe + len(self.queue))  # requêtes actives + file
                serveur.traite(requete)
                self.nb_attente -= 1
                return
        # mise en attente FIFO
        self.queue.append(requete)
        self.echeancier.update_L(self.nb_occupe + len(self.queue))  # on ajoute à la file

    def notify(self, serveur_libere):
        # libération → on décrémente puis tente de traiter la tête de file
        self.update_L()
        self.nb_occupe -= 1
        self.echeancier.update_L(self.nb_occupe + len(self.queue))  # après libération

        if self.queue:
            req = self.queue.pop(0)
            self.route_requete(req)
