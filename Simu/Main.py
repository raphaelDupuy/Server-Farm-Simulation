from Client import Client
from Routeur import Routeur
from Serveur import Serveur
from Echeancier import Echeancier, Ev
import matplotlib.pyplot as plt
import numpy as np


def initialise_ferme(nb_groupes, echeancier) -> Routeur:
    rout = Routeur(nb_groupes, echeancier)
    groupes = []
    serv_par_grp = 12//nb_groupes
    for i in range(nb_groupes):
        spe = []

        match nb_groupes:
            case 1:
                lambda_serv = 4/20
            case 2:
                lambda_serv = 7/20
            case 3:
                lambda_serv = 10/20
            case 6:
                lambda_serv = 14/20

        for _ in range (serv_par_grp):
            spe.append(Serveur(echeancier , lambda_serv, rout, i))

        groupes.append(spe)

    rout.add_groupes(groupes)

    return rout

def simulation(duree, lambda_client, nb_groupes):
    ech = Echeancier()
    rout = Routeur(nb_groupes, ech)

    # initialisation des groupes de serveurs
    groupes = []
    serv_par_grp = 12 // nb_groupes
    lambda_map = {1: 4/20, 2: 7/20, 3: 10/20, 6: 14/20}
    lambda_serv = lambda_map[nb_groupes]
    for spe in range(nb_groupes):
        grp = [Serveur(ech, lambda_serv, rout, spe) for _ in range(serv_par_grp)]
        groupes.append(grp)
    rout.add_groupes(groupes)

    # création du client
    client = Client(rout, lambda_client, ech)

    # simulation
    while ech.temps_actuel < duree and not ech.est_vide():
        ev, details = ech.prochain_evenement()

        # calcul pour l'aire sous L(t)
        delta_t = ech.temps_actuel - rout.t_precedent
        nb_L = rout.nb_attente + rout.nb_occupe
        rout.aire_L += nb_L * delta_t
        rout.t_precedent = ech.temps_actuel

        # gestion des événements
        if ev == Ev.NR:
            client.envoie_requete()
        elif ev == Ev.RAR:
            rout.route_requete(details)
        elif ev == Ev.FT:
            details[0].fin_traitement()

    return rout, ech



def calcule_delta(data):
    delta = dict()
    for temps, id, event in data:
        if not event:
            delta[id] = - temps
        else:
            delta[id] += temps

    delta = {id: dt for id, dt in delta.items() if dt >= 0}
    return delta

def calcule_moyenne(data):
    avg = 0
    lenght = 0
    for value in data.values():
        if value > 0:
            lenght += 1
            avg += value

    return (avg / lenght)

def plot_temps_reponse(n_simulations=2):
    for i, nb_groupes in enumerate([1, 2, 3, 6]):
        moyennes = []
        ic_95 = []

        for lb in lambdas:
            print(f"λ = {lb}, Groupes = {nb_groupes}")
            temps_reponses = []

            for _ in range(n_simulations):
                rout, ech = simulation(temps_max, lb, nb_groupes)

                nb_traitees = rout.nb_total - rout.perte
                duree = ech.temps_actuel

                if duree > 0 and nb_traitees > 0:
                    lambda_effectif = nb_traitees / duree  
                    L_moyen = rout.aire_L / duree          

                    D = L_moyen / lambda_effectif
                    if not np.isnan(D) and not np.isinf(D):
                        temps_reponses.append(D)

            if temps_reponses:
                moyenne = np.mean(temps_reponses)
                ecart_type = np.std(temps_reponses, ddof=1)
                intervalle = 1.96 * (ecart_type / np.sqrt(len(temps_reponses)))
            else:
                moyenne = 0
                intervalle = 0

            moyennes.append(moyenne)
            ic_95.append(intervalle)

        plt.errorbar(lambdas, moyennes, yerr=ic_95, fmt='-', color=couleurs[i], label=f"{nb_groupes} groupes")

    plt.xlabel("λ (taux d’arrivée des requêtes)")
    plt.ylabel("Temps de réponse moyen (s)")
    plt.title("Temps de réponse moyen (loi de Little, λ corrigé) en fonction de λ")
    plt.grid(True)
    plt.legend(title="Nb Groupes")
    plt.show()



def plot_taux_perte():
    plt.figure()
    for i, C in enumerate(groupes_list):
        pertes_pct = []
        for lb in lambdas:
            print(lb)
            moy = []
            for _ in range(1):
                rout, _ = simulation(temps_max, lb, C)
                print(f"Fin de la simulation:\n - Requêtes traitées: {rout.nb_total - rout.perte}\n - Requêtes perdues: {rout.perte}")
                moy.append(100 * rout.perte / rout.nb_total)
            moy = np.mean(moy)
            if moy > 0:
                pertes_pct.append(moy)
            else:
                pertes_pct.append(0)
        plt.plot(lambdas, pertes_pct, '-', color=couleurs[i], label=f"C={C}")

    plt.xlabel("λ (taux d’arrivée des requêtes)")
    plt.ylabel("Pourcentage de pertes (%)")
    plt.title("Taux de perte des requêtes en fonction de λ et C")
    plt.grid(True)
    plt.legend(title="Nombre de groupes (C)")
    plt.show()

def trouver_optimal_C(n_simulations=5, alpha=1.0, beta=100.0):
    resultats = []

    for lb in lambdas:
        scores_C = {}

        for C in groupes_list:
            temps_reponses = []
            pertes = []

            for _ in range(n_simulations):
                rout, ech = simulation(temps_max, lb, C)

                if ech.temps_actuel > 0 and rout.nb_total > 0:
                    L = rout.aire_L / ech.temps_actuel
                    lambda_eff = rout.nb_total / ech.temps_actuel
                    D = L / lambda_eff if lambda_eff > 0 else 0
                    perte = rout.perte / rout.nb_total

                    temps_reponses.append(D)
                    pertes.append(perte)

            if temps_reponses and pertes:
                D_mean = np.mean(temps_reponses)
                P_mean = np.mean(pertes)
                D_std = np.std(temps_reponses, ddof=1)
                P_std = np.std(pertes, ddof=1)

                score_mean = alpha * D_mean + beta * P_mean
                score_ic = 1.96 * np.sqrt((alpha * D_std) ** 2 + (beta * P_std) ** 2) / np.sqrt(n_simulations)

                scores_C[C] = (score_mean, score_ic)

        meilleur_C = min(scores_C.items(), key=lambda x: x[1][0] + x[1][1])[0]
        resultats.append((lb, meilleur_C, scores_C))

    return resultats

def plot_C_optimal_vs_lambda(n_simulations=5, alpha=1.0, beta=100.0):
    resultats = trouver_optimal_C(n_simulations, alpha, beta)

    lambdas_x = [lb for lb, _, _ in resultats]
    C_optimal = [C for _, C, _ in resultats]

    plt.figure(figsize=(10, 5))
    plt.step(lambdas_x, C_optimal, where='post', color='blue', label="C optimal")
    plt.scatter(lambdas_x, C_optimal, color='blue')
    
    plt.xlabel("λ (taux d’arrivée des requêtes)")
    plt.ylabel("Nombre de groupes C optimal")
    plt.title("Nombre de groupes C optimal en fonction de λ (avec IC 95%)")
    plt.yticks([1, 2, 3, 6])
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":

    couleurs = ['blue', 'green', 'red', 'orange']
    lambdas = [i for i in range(1, 7)]
    temps_max = 1000
    groupes_list = [1, 2, 3, 6]

    plot_C_optimal_vs_lambda(3, 1, 10)
