from Requete import Requete
from Echeancier import Echeancier, Evenement as Ev
from random import expovariate

class Serveur:

    # status = 1 -> Serveur peut prendre une requête
    # status = 0 -> Serveur occuppé
    # spe = 0 -> serveur non spécialisé (Voir classe Requete sinon)
    def __init__(self, echeancier : Echeancier, lambda_serv, spe=0):
        self.echeancier = echeancier
        self.lambda_serv = lambda_serv
        self.spe = spe
        self.occupe = False

    def __str__(self):
        status = "On" if self.occupe else "Off" 
        return f"Serveur -status: {status} | -spe: {self.get_spe()}\n"
    
    def get_spe(self):
        if spe := self.spe:
            return Requete(spe).name
        else:
            return None

    def traite(self, requete):
        if not self.occupe:
            if (requete.value == self.spe):
                self.occupe = True
                temps_traitement = self.echeancier.temps_actuel + expovariate(self.lambda_serv)
                self.echeancier.ajouter_evenement(temps_traitement, Ev.FT, (self, requete))
                print("Requête correspond à la spécialisation du serveur")
            else:
                MemoryError(f"Mauvaise spécialisation pour se serveur: {requete.value} != {self.spe}")

        else:
            MemoryError("Serveur occuppé")

    def fin_traitement(self):
        self.occupe = False