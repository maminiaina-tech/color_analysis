import numpy as np
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

from constants import RANDOM_STATE, K_MIN, K_MAX


# ============================================================
# Classe dédiée au clustering.
# ============================================================

class ClusteringService:
    """
    Cette classe s'occupe :
    - du choix automatique du nombre de clusters ;
    - de l'entraînement de KMeans ;
    - de la prédiction des labels.
    """

    def __init__(
        self,
        random_state: int = RANDOM_STATE,
        n_init: int = 10
    ):
        """
        Constructeur de la classe.

        Paramètres :
        - random_state : graine aléatoire.
        - n_init : nombre d'initialisations KMeans.
        """

        # Graine aléatoire pour la reproductibilité.
        self.random_state = random_state

        # Nombre d'initialisations de KMeans.
        # Une valeur plus élevée donne souvent un meilleur résultat,
        # mais augmente le temps de calcul.
        self.n_init = n_init

    # ========================================================
    # Choix automatique du nombre de clusters.
    # ========================================================

    def choose_best_k(
        self,
        pixels_lab: np.ndarray,
        k_min: int = K_MIN,
        k_max: int = K_MAX
    ):
        """
        Cette fonction choisit automatiquement le nombre de clusters.

        Méthode :
        - tester plusieurs valeurs de K ;
        - calculer le score de silhouette ;
        - conserver le K ayant le meilleur score.

        Étapes :
        1. Parcourir les valeurs possibles de K.
        2. Entraîner KMeans pour chaque K.
        3. Calculer le score silhouette.
        4. Retourner le meilleur K.
        """

        # Initialisation du meilleur K.
        best_k = k_min

        # Initialisation du meilleur score.
        best_score = -1.0

        # Étape 1 : tester plusieurs valeurs de K.
        for k in range(k_min, k_max + 1):

            # Sécurité : il faut au moins K pixels.
            if len(pixels_lab) < k:
                break

            # Étape 2 : création du modèle KMeans.
            kmeans = KMeans(
                n_clusters=k,
                n_init=self.n_init,
                random_state=self.random_state
            )

            # Entraînement et prédiction des labels.
            labels = kmeans.fit_predict(pixels_lab)

            # Sécurité : il faut au moins 2 clusters non vides
            # pour calculer un score silhouette.
            if len(np.unique(labels)) < 2:
                continue

            # Étape 3 : calcul du score silhouette.
            # On utilise un échantillon pour accélérer le calcul.
            sample_size = min(5000, len(pixels_lab))

            score = silhouette_score(
                pixels_lab,
                labels,
                sample_size=sample_size,
                random_state=self.random_state
            )

            # Étape 4 : mise à jour du meilleur K.
            if score > best_score:
                best_score = score
                best_k = k

        return best_k, best_score

    # ========================================================
    # Entraînement KMeans.
    # ========================================================

    def fit(self, pixels_lab: np.ndarray, k: int) -> KMeans:
        """
        Cette fonction entraîne KMeans sur les pixels LAB.

        Étapes :
        1. Créer un modèle KMeans avec K clusters.
        2. Entraîner le modèle.
        3. Retourner le modèle entraîné.
        """

        # Étape 1 : création du modèle.
        kmeans = KMeans(
            n_clusters=k,
            n_init=self.n_init,
            random_state=self.random_state
        )

        # Étape 2 : entraînement.
        kmeans.fit(pixels_lab)

        # Étape 3 : retour du modèle.
        return kmeans

    # ========================================================
    # Prédiction des clusters.
    # ========================================================

    def predict(
        self,
        kmeans: KMeans,
        pixels_lab: np.ndarray
    ) -> np.ndarray:
        """
        Cette fonction prédit le cluster de chaque pixel.

        Étapes :
        1. Utiliser le modèle KMeans entraîné.
        2. Prédire les labels.
        3. Retourner les labels.
        """

        # Étape 1 et 2 : prédiction.
        labels = kmeans.predict(pixels_lab)

        # Étape 3 : retour des labels.
        return labels