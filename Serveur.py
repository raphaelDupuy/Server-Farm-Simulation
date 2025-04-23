from Routeur import Routeur
from Echeancier import Echeancier, Evenement as Ev
from random import expovariate

class Serveur:

    # status = 1 -> Serveur peut prendre une requête
    # status = 0 -> Serveur occuppé
    # spe = None -> serveur non spécialisé (Voir classe Requete sinon)
    def __init__(self, echeancier : Echeancier, lambda_serv, routeur : Routeur, spe=None):
        self.echeancier = echeancier
        self.lambda_serv = lambda_serv
        self.spe = spe
        self.occupe = False
        self.routeur = routeur

    def __str__(self):
        status = "Occupé" if self.occupe else "Libre" 
        return f"Serveur -status: {status} | -spe: {self.get_spe()}\n"
    
    def get_spe(self):
        return self.spe

    def traite(self, requete):
        if not self.occupe:
            if (requete.get_value() == self.spe):
                self.occupe = True
                temps_traitement = self.echeancier.temps_actuel + expovariate(self.lambda_serv)
                self.echeancier.ajouter_evenement(temps_traitement, Ev.FT, (self, requete))
                self.echeancier.ajouter_historique(temps_traitement, requete.get_id(), 1)
            else:
                MemoryError(f"Mauvaise spécialisation pour se serveur: {requete.value} != {self.spe}")

        else:
            MemoryError("Serveur occuppé")

    def fin_traitement(self):
        self.routeur.notify(self.spe)
        self.occupe = False
