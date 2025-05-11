from heapq import heappush, heappop
import random
import time
import numpy as np
import matplotlib.pyplot as plt

class Echeancier:
    def __init__(self):
        self.events = []  # File de priorité des événements
        self.temps_actuel = 0
        self.historique = []
        # petit = plus prioritaire
        self.priorites = {"FIN": 0, "ROUTAGE": 1, "ARRIVEE": 2}

    def ajouter_evenement(self, temps, type_evt, details=None):
        # trie d'abord par temps, puis par priorité si temps égaux
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
    # Paramètres de service
    lambda_map = {1:4/20, 2:7/20, 3:10/20, 6:14/20}
    lambda_serv = lambda_map[nb_groupes]
    temps_routage = (nb_groupes - 1) / nb_groupes

    # État du système
    ech = Echeancier()
    file_routeur = []
    serveurs_occupe = [False] * (12//nb_groupes) * nb_groupes  # État serveurs
    nb_total = 0      # Nb total requetes
    nb_pertes = 0     # Nb requetes perdues
    historique = {}
    id_requete = 0
    stop = 0
    en_routage = None # routeur occupé ou pas

    # Première arrivée
    ech.ajouter_evenement(0, "ARRIVEE", id_requete)

    while ech.temps_actuel < duree_max:
        stop += 1
        temps, evt_type, details = ech.prochain_evenement()
        
        # print(f"Temps: {temps:.2f}, Événement: {evt_type}, Détails: {details}")
        match evt_type:
            case "ARRIVEE":
                nb_total += 1

                nb_occupe = 0
                for serv in serveurs_occupe:
                    if serv:
                        nb_occupe += 1
                if (len(file_routeur) + nb_occupe) < 100: # + nb de serveurs occupés
                    spe = random.randint(0, nb_groupes-1)  # spe aléatoire
                    file_routeur.append((spe, temps, details))  # (spe, temps_arrivee, id_requete)
                    historique[temps] = {"entree": temps, "debut_service": None, "fin": None}
                    if en_routage == None:
                        
                        ech.ajouter_evenement(temps + temps_routage, "ROUTAGE", (spe, details))
                        en_routage = (spe, details)

                else:
                    nb_pertes += 1

                id_requete += 1
                ech.ajouter_evenement(temps + random.expovariate(lambda_client), "ARRIVEE", id_requete)

            case "ROUTAGE":
                # print(f"ROUTAGE {en_routage}")
                
                if file_routeur:
                    spe, t_arr, id = file_routeur[0]
                    # print(f"details: {id}")
                    if details[1] != id:
                        print(f"Erreur de routage: {details[1]} != {id}")

                    debut_groupe = spe * (12//nb_groupes)
                    fin_groupe = debut_groupe + (12//nb_groupes)
                    serveur_trouve = False
                    for i in range(debut_groupe, fin_groupe):
                        if not serveurs_occupe[i]:
                            # print(f"Serveur {i} libre, traitement de la requête")
                            serveurs_occupe[i] = True
                            file_routeur.pop(0)
                            t_fin = temps + random.expovariate(lambda_serv)
                            ech.ajouter_evenement(t_fin, "FIN", (i, details))
                            historique[t_arr]["debut_service"] = temps
                            if len(file_routeur) > 0:
                                next = file_routeur[0]
                                ech.ajouter_evenement(temps + temps_routage, "ROUTAGE", (next[0], next[2]))
                            else:
                                en_routage = None
                            serveur_trouve = True
                            break
                        
                    if not serveur_trouve:
                        # print("Aucun serveur libre, requête en attente")
                        for evt in ech.events:
                            if evt[2] == "FIN":
                                ech.ajouter_evenement(evt[0], "ROUTAGE", details)
                                break
                                

            case "FIN":
                # print("details", details)
                serveur_id = details[0]

                serveurs_occupe[serveur_id] = False
                historique[t_arr]["fin"] = temps


    temps_reponse = []
    for infos in historique.values():
        if infos["fin"] is not None:
            temps_reponse.append(infos["fin"] - infos["entree"])
    temps_moyen = np.mean(temps_reponse) if temps_reponse else 0
    taux_perte = nb_pertes / nb_total if nb_total > 0 else 0

    return temps_moyen, taux_perte

if __name__ == "__main__":
    
    lambdas = np.arange(0.1, 7.1, 0.2)  # Valeurs de lambda à tester
    nb_groupes_list = [1, 2, 3, 6]      # Valeurs de C
    couleurs = ['blue', 'green', 'red', 'orange']
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 12))
    
    for i, C in enumerate(nb_groupes_list):
        temps_reponse = []
        taux_pertes = []
        
        for lb in lambdas:
            tr, tp = simulation(lb, C, 1000)
            temps_reponse.append(tr)
            taux_pertes.append(tp)
            print(f"C={C}, λ={lb:.1f}, TR={tr:.2f}, TP={tp:.2%}")
        
        ax1.plot(lambdas, temps_reponse, '-', color=couleurs[i], label=f"C={C}")
        ax2.plot(lambdas, taux_pertes, '-', color=couleurs[i], label=f"C={C}")
    
    # temps reponse
    ax1.set_xlabel("λ (taux d'arrivée des requêtes)")
    ax1.set_ylabel("Temps de réponse moyen (s)")
    ax1.set_title("Évolution du temps de réponse moyen en fonction de λ")
    ax1.grid(True)
    ax1.legend()
    
    #taux perte
    ax2.set_xlabel("λ (taux d'arrivée des requêtes)")
    ax2.set_ylabel("Taux de perte")
    ax2.set_title("Évolution du taux de perte en fonction de λ")
    ax2.grid(True)
    ax2.legend()
    
    plt.tight_layout()
    plt.show()