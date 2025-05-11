# Description du système

Le projet a pour but de simuler une ferme de 12 serveurs avec un routage des requêtes reçues, dans le but d'étudier l'impact de différentes configurations de groupes de serveurs sur les performances du système.

### Caractéristiques principales

- Nombre de serveurs : 12 serveurs identiques
- Configurations possibles (groupes C) : 1, 2, 3 ou 6 groupes
- File d'attente du routeur : Capacité de 100 requêtes
- Politique de service : FIFO (First In First Out)

# Structure du code

### Gestion des événements (class Echeancier)

- Maintient une liste ordonnée des événements
- Méthodes principales :
    - ajouter_evt() : Ajoute un nouvel événement
    - prochain_evt() : Récupère le prochain événement à traiter
    - vider() : Réinitialise l'échéancier

### Simulation principale (simulation())

- Types d'événements
    - ARRIVEE
        - Gère les arrivées de requêtes avec une loi exponentielle de paramètre λ
        - Gère le rejet si file pleine
        - Planifie le routage si possible
        - Attribue aux requêtes une spécialisation selon la loi uniforme

    - ROUTAGE
        - Temps de traitement constant : (C-1)/C
        - Dirige les requêtes vers le groupe approprié
        - Bloque si aucun serveur n'est libre

    - FIN
        - Libère le serveur que la requête occupait

### Calcul des métriques

#### Temps de réponse

    temps_moyen = temps_fin - temps_arrivee

- Mesure le temps de réponse moyen dans le système, et permet donc d'évaluer la performance globale des différentes configuration de groupes pour des lambdas différents.

#### Loi de Little

    temps_moyen = nb_moyen_clients / lambda_effectif

- Calcul différent plus juste du temps moyen de réponse grâce à la loi de Little.

#### Taux de perte

    taux_perte = nb_rejets / nb_total_requetes

- On calcul ici le taux de perte pour chaque configuration de groupes en fonction de lambda différents. 


# Paramètres clés

### Temps de service

Selon le nombre de groupes C :

- C=1 : μ = 4/20
- C=2 : μ = 7/20
- C=3 : μ = 10/20
- C=6 : μ = 14/20

### Paramètres de simulation

Ce sont les paramètres utilisées lors de l'appel de la fonction principale simulation() :

- lambda_client : un des taux d'arrivée lambda, obtenus avec :

        np.arange(0.1, 2.1, 0.1)

- nb_groupes : les différentes valeurs de groupe sur lesquelles on fera la simulation :

        1, 2, 3 et 6

- duree_max : une durée maximale pour arreter le programme (la même pour toute une simulation, pour avoir des résultats cohérents)

# Utilisation

    python Simu/Main.py

Les résultats de la simulation sont automatiquement générés et affichés sous forme de graphiques, permettant de comparer les différentes configurations et déterminer la valeur optimale de C pour chaque λ.

## Collaborateurs

- Raphael Dupuy
- Cyriac Thibaudeau