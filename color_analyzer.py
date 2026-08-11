# color_analyzer.py

from typing import List, Tuple
import numpy as np

from constants import (
    MAX_SAMPLES,
    K_MIN,
    K_MAX,
    RANDOM_STATE
)

from models import ColorResult, AnalysisMetadata

from image_processor import ImageProcessor
from color_processor import ColorProcessor
from clustering_service import ClusteringService


# ============================================================
# Classe principale d'analyse colorimétrique.
# ============================================================

class ColorAnalyzer:
    """
    Cette classe orchestre tout le pipeline d'analyse :

    1. conversion RGB -> LAB ;
    2. échantillonnage des pixels ;
    3. choix du nombre de clusters ;
    4. clustering KMeans ;
    5. calcul des proportions ;
    6. conversion LAB -> RGB ;
    7. reconstruction de l'image segmentée ;
    8. nommage des couleurs ;
    9. création des résultats.
    """

    def __init__(
        self,
        image_processor: ImageProcessor | None = None,
        color_processor: ColorProcessor | None = None,
        clustering_service: ClusteringService | None = None
    ):
        """
        Constructeur de la classe.

        On utilise l'injection de dépendances.
        Cela permet de faciliter les tests et la maintenance.
        """

        # Processeur d'image.
        self.image_processor = image_processor or ImageProcessor()

        # Processeur de couleurs.
        self.color_processor = color_processor or ColorProcessor()

        # Service de clustering.
        self.clustering_service = clustering_service or ClusteringService()

    # ========================================================
    # Fonction principale d'analyse.
    # ========================================================

    def analyze(
        self,
        image_rgb: np.ndarray,
        mode: str,
        fixed_k: int = 6,
        max_samples: int = MAX_SAMPLES
    ) -> Tuple[List[ColorResult], np.ndarray, AnalysisMetadata]:
        """
        Cette fonction analyse une image RGB et retourne :

        - la liste des couleurs dominantes ;
        - l'image segmentée ;
        - les métadonnées de l'analyse.
        """

        # ====================================================
        # Étape 1 : récupérer les dimensions de l'image.
        # ====================================================
        height, width, _ = image_rgb.shape

        # ====================================================
        # Étape 2 : conversion de l'image RGB vers LAB.
        # ====================================================
        # LAB est plus adapté que RGB pour une analyse
        # proche de la perception humaine.
        image_lab = self.color_processor.rgb_image_to_lab(image_rgb)

        # ====================================================
        # Étape 3 : transformer l'image en liste de pixels.
        # ====================================================
        # Image LAB de forme (H, W, 3)
        # devient une liste de pixels de forme (H*W, 3).
        pixels_lab = image_lab.reshape(-1, 3)

        # ====================================================
        # Étape 4 : échantillonnage des pixels.
        # ====================================================
        # On utilise un sous-ensemble de pixels pour accélérer
        # l'entraînement KMeans.
        fit_pixels = self.image_processor.sample_pixels(
            pixels_lab,
            max_samples=max_samples,
            random_state=RANDOM_STATE
        )

        # ====================================================
        # Étape 5 : choix du nombre de clusters.
        # ====================================================
        if mode == "Automatique":
            # Mode automatique :
            # on utilise le score silhouette pour choisir K.
            k, score = self.clustering_service.choose_best_k(
                fit_pixels,
                k_min=K_MIN,
                k_max=K_MAX
            )
        else:
            # Mode manuel :
            # K est choisi par l'utilisateur.
            k = int(fixed_k)
            score = None

        # ====================================================
        # Étape 6 : entraînement KMeans.
        # ====================================================
        kmeans = self.clustering_service.fit(
            fit_pixels,
            k=k
        )

        # ====================================================
        # Étape 7 : prédiction des clusters pour tous les pixels.
        # ====================================================
        labels = self.clustering_service.predict(
            kmeans,
            pixels_lab
        )

        # ====================================================
        # Étape 8 : récupération des centres des clusters.
        # ====================================================
        # Les centres sont dans l'espace LAB.
        centers_lab = kmeans.cluster_centers_

        # ====================================================
        # Étape 9 : comptage des pixels par cluster.
        # ====================================================
        counts = np.bincount(labels, minlength=k)

        # ====================================================
        # Étape 10 : calcul des proportions.
        # ====================================================
        proportions = counts / counts.sum()

        # ====================================================
        # Étape 11 : conversion des centres LAB vers RGB.
        # ====================================================
        centers_rgb = self.color_processor.lab_centers_to_rgb(
            centers_lab
        )

        # ====================================================
        # Étape 12 : reconstruction de l'image segmentée.
        # ====================================================
        segmented_rgb = self.image_processor.rebuild_image_from_labels(
            labels=labels,
            colors=centers_rgb,
            height=height,
            width=width
        )

        # ====================================================
        # Étape 13 : tri des couleurs par proportion décroissante.
        # ====================================================
        order = np.argsort(-proportions)

        # Liste qui contiendra les résultats finaux.
        couleurs: List[ColorResult] = []

        # ====================================================
        # Étape 14 : création des objets ColorResult.
        # ====================================================
        for rank, cluster_idx in enumerate(order, start=1):

            # Nommage approximatif de la couleur.
            name, distance = self.color_processor.get_color_name(
                centers_lab[cluster_idx]
            )

            # Conversion du centre RGB en liste Python.
            rgb = centers_rgb[cluster_idx].tolist()

            # Conversion RGB -> HEX.
            hex_value = self.color_processor.rgb_to_hex(
                centers_rgb[cluster_idx]
            )

            # Création de l'objet résultat.
            color_result = ColorResult(
                rang=rank,
                nom=name,
                rgb=rgb,
                hex=hex_value,
                pixels=int(counts[cluster_idx]),
                proportion=float(proportions[cluster_idx]),
                proportion_pct=round(
                    float(proportions[cluster_idx] * 100),
                    2
                ),
                distance_lab=round(float(distance), 2)
            )

            couleurs.append(color_result)

        # ====================================================
        # Étape 15 : création des métadonnées de l'analyse.
        # ====================================================
        metadata = AnalysisMetadata(
            hauteur=height,
            largeur=width,
            nombre_total_pixels=height * width,
            mode_clustering=mode,
            nombre_clusters=k,
            score_silhouette=float(score) if score is not None else None
        )

        # ====================================================
        # Étape 16 : retour des résultats.
        # ====================================================
        return couleurs, segmented_rgb, metadata