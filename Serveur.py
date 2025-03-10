import Requete

class Serveur():

    # status = 1 -> Serveur peut prendre une requête
    # status = 0 -> Serveur occuppé
    # spe = 0 -> serveur non spécialisé (Voir classe Requete sinon)
    def __init__(self, spe=0):
        self.status = 1
        self.spe = spe

    def traite(self, requete):
        if not self.spe:
            print("Serveur non spécialisé, traîte toutes les requêtes")
        if (requete.value == self.spe):
            print("Requête correspond à la spécialisation du serveur")