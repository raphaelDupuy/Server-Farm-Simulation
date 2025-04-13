from Requete import Requete
from Echeancier import Echeancier, Evenement as Ev
from random import expovariate

class Routeur():

    def __init__(self, nb_groupes, echeancier : Echeancier):

        if not nb_groupes in {1, 2, 3, 6}:
            raise ValueError("Nombre de groupes incorrect")
        else:
            self.nb_groupes = nb_groupes
            self.temps_traitement = (nb_groupes - 1)/nb_groupes
 
        self.echeancier = echeancier
        self.nb_attente = 0
        self.perte = 0
        self.nb_total = 0
        self.bloque = None

    def add_groupes(self, groupes):
        self.groupes = groupes

    def notify(self, spe):
        if self.bloque:
            print(self.bloque)
            if self.bloque[0] == spe:
                requete = self.bloque[1]
                print("débloqué")
                self.bloque = None
                self.route_requete(requete)

    def __str__(self):
        res_str = "===========:Routeur:===========\n"
        cnt = 1
        for grp in self.groupes:
            res_str += f"------------Groupe {cnt}-----------\n"
            cnt += 1
            for serv in grp:
                res_str += serv.__str__()
        res_str += "===============================\n"

        return res_str
    

    def ajoute_requete(self, requete):

        self.nb_total += 1

        if self.nb_attente < 100:
            temps_traitement = self.echeancier.temps_actuel + expovariate(self.temps_traitement)

            self.echeancier.ajouter_evenement(temps_traitement, Ev.RAR, (self, requete))
            self.nb_attente += 1
            print(f"---- En attente : {self.nb_attente}")

        else:
            self.perte += 1
            print(f"Requête perdue {requete}")

    def route_requete(self, requete):
        if self.bloque == None:
            spe = requete.value
            trouve = False
            print(f"routage requete {spe}")
            for serveur in self.groupes[spe]:
                if (not serveur.occupe):
                    serveur.traite(requete)
                    self.nb_attente -= 1
                    print(f"serveur trouvé pour la requête {spe}")
                    trouve = True
                    break
            if not trouve:
                print("bloqué")
                print(self)
                self.bloque = (spe, requete)
        else:
            print("Routeur en attente de libération")
