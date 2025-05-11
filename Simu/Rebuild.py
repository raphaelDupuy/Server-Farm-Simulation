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
        temps_moyen, taux_perte, W_little
    """
    # Paramètres
    lambda_map = {1:4/20, 2:7/20, 3:10/20, 6:14/20}
    lambda_serv = lambda_map[nb_groupes]
    temps_routage = (nb_groupes - 1) / nb_groupes

    # Etat système
    ech = Echeancier()
    file_routeur = []
    serveurs_occupe = [False] * (12//nb_groupes) * nb_groupes  # Etat serveurs
    nb_total = 0      # Nb total requetes
    nb_pertes = 0     # Nb requetes perdues
    historique = {}
    id_requete = 0
    stop = 0
    en_routage = None # Routeur occupé ou pas

    # Variables loi de Little
    nb_requetes_cumul = 0
    dernier_temps = 0
    nb_requetes = 0        # Nb actuel de requetes dans le système

    # Première arrivée
    ech.ajouter_evenement(0, "ARRIVEE", id_requete)

    while ech.temps_actuel < duree_max:
        stop += 1
        temps, evt_type, details = ech.prochain_evenement()
        
        # Maj du nombre moyen de requêtes
        nb_requetes_cumul += nb_requetes * (temps - dernier_temps)
        dernier_temps = temps
        
        # print(f"Temps: {temps:.2f}, Événement: {evt_type}, Détails: {details}")
        match evt_type:
            case "ARRIVEE":
                nb_total += 1

                nb_occupe = 0
                for serv in serveurs_occupe:
                    if serv:
                        nb_occupe += 1
                if (len(file_routeur) + nb_occupe) < 100:
                    spe = random.randint(0, nb_groupes-1)  # spe aléatoire
                    file_routeur.append((spe, temps, details))  # (spe, temps_arrivee, id_requete)
                    historique[temps] = {"entree": temps, "debut_service": None, "fin": None}
                    if en_routage == None:
                        
                        ech.ajouter_evenement(temps + temps_routage, "ROUTAGE", (spe, details))
                        en_routage = (spe, details)
                    nb_requetes += 1  # requete entre dans le système

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
                nb_requetes -= 1  # requete sort du système


    temps_reponse = []
    for infos in historique.values():
        if infos["fin"] is not None:
            temps_reponse.append(infos["fin"] - infos["entree"])
    temps_moyen = np.mean(temps_reponse) if temps_reponse else 0
    taux_perte = nb_pertes / nb_total if nb_total > 0 else 0

    # Loi de Little
    L = nb_requetes_cumul / duree_max 
    lambda_effectif = (nb_total - nb_pertes) / duree_max
    W_little = L / lambda_effectif if lambda_effectif > 0 else 0

    return temps_moyen, taux_perte, W_little

def plot_temps_reponse(lambdas, resultats):
    """Plot le temps de réponse moyen avec IC à 95%"""
    plt.figure(figsize=(10, 6))
    couleurs = ['blue', 'green', 'red', 'orange']
    
    for i, C in enumerate(resultats.keys()):
        temps_moyen = [np.mean(tr) for tr in resultats[C]]

        ic_95 = [1.96 * np.std(tr) / np.sqrt(len(tr)) if len(tr) > 1 else 0 
                 for tr in resultats[C]]
        
        plt.errorbar(lambdas, temps_moyen, yerr=ic_95, fmt='-', 
                    color=couleurs[i], label=f"C={C}", capsize=5)
    
    plt.xlabel("λ (taux d'arrivée des requêtes)")
    plt.ylabel("Temps de réponse moyen (s)")
    plt.title("Évolution du temps de réponse moyen en fonction de λ")
    plt.grid(True)
    plt.legend()

def plot_taux_perte(lambdas, taux_pertes):
    """Plot le taux de perte"""
    plt.figure(figsize=(10, 6))
    couleurs = ['blue', 'green', 'red', 'orange']
    
    for i, C in enumerate(taux_pertes.keys()):
        plt.plot(lambdas, taux_pertes[C], '-', 
                color=couleurs[i], label=f"C={C}")
    
    plt.xlabel("λ (taux d'arrivée des requêtes)")
    plt.ylabel("Taux de perte")
    plt.title("Évolution du taux de perte en fonction de λ")
    plt.grid(True)
    plt.legend()

def plot_temps_little(lambdas, resultats_little):
    """Plot le temps moyen calculé avec la loi de Little"""
    plt.figure(figsize=(10, 6))
    couleurs = ['blue', 'green', 'red', 'orange']
    
    for i, C in enumerate(resultats_little.keys()):
        temps_little = [np.mean(w) for w in resultats_little[C]]

        ic_95 = [1.96 * np.std(w) / np.sqrt(len(w)) if len(w) > 1 else 0 
                 for w in resultats_little[C]]
        
        plt.errorbar(lambdas, temps_little, yerr=ic_95, fmt='-', 
                    color=couleurs[i], label=f"C={C}", capsize=5)
    
    plt.xlabel("λ (taux d'arrivée des requêtes)")
    plt.ylabel("Temps moyen (Loi de Little)")
    plt.title("Évolution du temps moyen (Little) en fonction de λ")
    plt.grid(True)
    plt.legend()

if __name__ == "__main__":
    lambdas = np.arange(0.5, 2.1, 0.05)
    nb_groupes_list = [1, 2, 3, 6]
    
    resultats = {C: [] for C in nb_groupes_list}
    taux_pertes = {C: [] for C in nb_groupes_list}
    resultats_little = {C: [] for C in nb_groupes_list}
    
    for C in nb_groupes_list:
        for lb in lambdas:
            temps_reponses = []
            temps_little = []
            tp_total = 0
            n_sims = 10
            
            for _ in range(n_sims):
                tr, tp, W_little = simulation(lb, C, 3000)
                temps_reponses.append(tr)
                temps_little.append(W_little)
                tp_total += tp
            
            resultats[C].append(temps_reponses)
            resultats_little[C].append(temps_little)
            taux_pertes[C].append(tp_total / n_sims)
            print(f"C={C}, λ={lb:.1f}, TR={np.mean(temps_reponses):.2f}, W_little={np.mean(temps_little):.2f}")
    
    plot_temps_reponse(lambdas, resultats)
    plot_taux_perte(lambdas, taux_pertes)
    plot_temps_little(lambdas, resultats_little)
    plt.show()