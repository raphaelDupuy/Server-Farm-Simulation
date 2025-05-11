from heapq import heappush, heappop
import random
import numpy as np

class Echeancier:
    def __init__(self):
        self.events = []  # File de priorité des événements
        self.temps_actuel = 0
        self.historique = []
        # Plus petit = plus prioritaire
        self.priorites = {"FIN": 0, "ROUTAGE": 1, "ARRIVEE": 2}

    def ajouter_evenement(self, temps, type_evt, details=None):
        # Le heap trie d'abord par temps, puis par priorité si temps égaux
        heappush(self.events, (temps, self.priorites[type_evt], type_evt, details))

    def prochain_evenement(self):
        if self.events:
            temps, _, type_evt, details = heappop(self.events)
            self.temps_actuel = temps
            return temps, type_evt, details
        return None

def simulation(lambda_client, nb_groupes, duree_max):
    """Simule la ferme de serveurs
    Args:
        lambda_client: taux d'arrivée des requêtes
        nb_groupes: nombre de groupes de serveurs (1,2,3 ou 6)
        duree_max: durée de simulation
    Returns:
        temps_moyen, taux_perte
    """
    # Paramètres de service selon le nombre de groupes
    lambda_map = {1:4/20, 2:7/20, 3:10/20, 6:14/20}
    lambda_serv = lambda_map[nb_groupes]
    temps_routage = (nb_groupes - 1) / nb_groupes

    # État du système
    ech = Echeancier()
    file_routeur = []  # File d'attente du routeur
    serveurs_occupe = [False] * (12//nb_groupes) * nb_groupes  # État des serveurs
    nb_total = 0      # Nombre total de requêtes
    nb_pertes = 0     # Nombre de requêtes perdues
    historique = {}   # Pour calculer les temps de réponse
    id_requete = 0
    stop = 0
    en_routage = None  # Indique si le routeur est occupé

    # Programme l'arrivée de la première requête
    ech.ajouter_evenement(0, "ARRIVEE", id_requete)

    # Boucle principale
    while ech.temps_actuel < duree_max:
        print(stop)
        stop += 1
        temps, evt_type, details = ech.prochain_evenement()
        
        print(f"Temps: {temps:.2f}, Événement: {evt_type}, Détails: {details}")
        match evt_type:
            case "ARRIVEE":
                # Nouvelle requête
                nb_total += 1

                if len(file_routeur) < 100: # + nb de serveurs occupés
                    print("Requête acceptée: taille de la file:", len(file_routeur))
                    spe = random.randint(0, nb_groupes-1)  # Spécialisation aléatoire
                    file_routeur.append((spe, temps, details))  # (spécialisation, temps_arrivee, id_requete)
                    historique[temps] = {"entree": temps, "debut_service": None, "fin": None}
                    if file_routeur:
                        # Si la file n'est pas vide, programme le routage
                        t_rar = temps + temps_routage
                        ech.ajouter_evenement(t_rar, "ROUTAGE", details)
                else:
                    print("Requête perdue")
                    nb_pertes += 1

                id_requete += 1
                # Programme prochaine arrivée
                ech.ajouter_evenement(temps + random.expovariate(lambda_client), "ARRIVEE", id_requete)

            case "ROUTAGE":
                if en_routage:
                    # Si le routeur est occupé, on ne fait rien
                    print("Routeur occupé, requête en attente")
                    en_routage = ()
                else:
                    if file_routeur:
                        spe, t_arr, id = file_routeur[0]
                        if details != id:
                            print(f"Erreur de routage: {details} != {id}")
                        # Cherche un serveur libre dans le bon groupe
                        debut_groupe = spe * (12//nb_groupes)
                        fin_groupe = debut_groupe + (12//nb_groupes)
                        serveur_trouve = False
                        for i in range(debut_groupe, fin_groupe):
                            if not serveurs_occupe[i]:
                                print(f"Serveur {i} libre, traitement de la requête")
                                # Serveur trouvé
                                serveurs_occupe[i] = True
                                file_routeur.pop(0)
                                t_fin = temps + random.expovariate(lambda_serv)
                                ech.ajouter_evenement(t_fin, "FIN", i)
                                historique[t_arr]["debut_service"] = temps
                                # Programme routage suivant si file non vide
                                en_routage = False
                                serveur_trouve = True
                                break
                            else:
                                print(f"Serveur {i} occupé")
                        # Dans le cas "ROUTAGE"
                        if not serveur_trouve:  # Si aucun serveur libre trouvé
                            print("Aucun serveur libre, requête en attente")
                            en_routage = True
                            ech.ajouter_evenement(temps, "ROUTAGE", details)

            case "FIN":
                # Libère le serveur
                en_routage = False
                serveur_id = details
                serveurs_occupe[serveur_id] = False
                historique[t_arr]["fin"] = temps
                # Si file non vide, programme routage
        print(ech.events)
    # Calcul statistiques
    temps_reponse = []
    for infos in historique.values():
        if infos["fin"] is not None:  # Requête complétée
            temps_reponse.append(infos["fin"] - infos["entree"])
    temps_moyen = np.mean(temps_reponse) if temps_reponse else 0
    taux_perte = nb_pertes / nb_total if nb_total > 0 else 0

    return temps_moyen, taux_perte

if __name__ == "__main__":
    # Test avec différentes configurations
    for nb_groupes in [1]:
        tr, tp = simulation(5, nb_groupes, 300)
        print(f"Groupes: {nb_groupes}, Temps moyen: {tr:.2f}, Taux perte: {tp:.2%}")