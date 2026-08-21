# tests/test_clustering_service.py

import numpy as np
import pytest
from sklearn.cluster import KMeans

from clustering_service import ClusteringService


# ============================================================
# Données synthétiques : 3 nuages de points bien séparés.
# ============================================================

@pytest.fixture
def trois_groupes():
    """150 points répartis en 3 groupes très éloignés."""
    rng = np.random.default_rng(42)
    groupe_a = rng.normal(0, 0.5, size=(50, 3))
    groupe_b = rng.normal(40, 0.5, size=(50, 3))
    groupe_c = rng.normal(-40, 0.5, size=(50, 3))
    return np.vstack([groupe_a, groupe_b, groupe_c])


# ============================================================
# Tests de l'entraînement KMeans.
# ============================================================

class TestFit:

    @pytest.fixture
    def service(self):
        return ClusteringService()

    def test_retourne_un_modele_kmeans(self, service, trois_groupes):
        kmeans = service.fit(trois_groupes, k=3)

        assert isinstance(kmeans, KMeans)

    def test_nombre_de_centres(self, service, trois_groupes):
        """Le modèle possède exactement K centres."""
        kmeans = service.fit(trois_groupes, k=3)

        assert kmeans.cluster_centers_.shape == (3, 3)

    def test_reproductibilite(self, service, trois_groupes):
        """Même graine => mêmes centres."""
        c1 = service.fit(trois_groupes, k=3).cluster_centers_
        c2 = service.fit(trois_groupes, k=3).cluster_centers_

        np.testing.assert_allclose(c1, c2)


# ============================================================
# Tests de la prédiction.
# ============================================================

class TestPredict:

    @pytest.fixture
    def service(self):
        return ClusteringService()

    def test_labels_pour_tous_les_pixels(self, service, trois_groupes):
        """Un label est retourné pour chaque pixel d'entrée."""
        kmeans = service.fit(trois_groupes, k=3)
        labels = service.predict(kmeans, trois_groupes)

        assert labels.shape == (len(trois_groupes),)
        assert set(np.unique(labels)).issubset({0, 1, 2})

    def test_points_proches_meme_cluster(self, service, trois_groupes):
        """Deux points identiques tombent dans le même cluster."""
        kmeans = service.fit(trois_groupes, k=3)
        point = trois_groupes[0:1]

        label_point = service.predict(kmeans, point)[0]
        label_copie = service.predict(kmeans, point * 1.0 + 1e-9)[0]

        assert label_point == label_copie


# ============================================================
# Tests du choix automatique du nombre de clusters.
# ============================================================

class TestChooseBestK:

    @pytest.fixture
    def service(self):
        return ClusteringService(n_init=4)

    def test_trouve_le_bon_k_sur_donnees_separees(
        self, service, trois_groupes
    ):
        """Sur 3 groupes bien séparés, le meilleur K est 3."""
        best_k, score = service.choose_best_k(
            trois_groupes, k_min=2, k_max=6
        )

        assert best_k == 3
        assert score > 0.8

    def test_score_dans_l_intervalle_valide(self, service, trois_groupes):
        """Le score silhouette est compris entre -1 et 1."""
        _, score = service.choose_best_k(trois_groupes, k_min=2, k_max=4)

        assert -1.0 <= score <= 1.0

    def test_respecte_les_bornes(self, service, trois_groupes):
        """Le K choisi reste dans [k_min, k_max]."""
        best_k, _ = service.choose_best_k(trois_groupes, k_min=2, k_max=3)

        assert 2 <= best_k <= 3

    def test_peu_de_pixels_que_de_clusters(self, service):
        """
        Avec moins de pixels que de clusters demandés,
        la boucle s'arrête proprement et retourne k_min.
        """
        pixels = np.zeros((2, 3))

        best_k, score = service.choose_best_k(pixels, k_min=2, k_max=8)

        assert best_k == 2
