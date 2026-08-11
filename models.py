from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Optional


# ============================================================
# Classe représentant une couleur dominante extraite.
# ============================================================

@dataclass
class ColorResult:
    """
    Cette classe stocke toutes les informations relatives
    à une couleur dominante détectée dans l'image.
    """

    # Position de la couleur dans le classement.
    # Exemple : 1 = couleur la plus présente.
    rang: int

    # Nom approximatif de la couleur.
    # Exemple : "bleu", "rouge", "gris".
    nom: str

    # Valeur RGB de la couleur dominante.
    # Exemple : [31, 78, 156]
    rgb: List[int]

    # Code hexadécimal de la couleur.
    # Exemple : "#1f4e9c"
    hex: str

    # Nombre de pixels appartenant à cette couleur.
    pixels: int

    # Proportion de pixels dans l'image.
    # Exemple : 0.342 signifie 34.2 %.
    proportion: float

    # Proportion en pourcentage.
    # Exemple : 34.2
    proportion_pct: float

    # Distance LAB entre la couleur extraite et la couleur
    # de référence utilisée pour le nommage.
    distance_lab: float

    def to_dict(self) -> Dict[str, Any]:
        """
        Convertit l'objet en dictionnaire.
        Utile pour l'export JSON.
        """
        return asdict(self)


# ============================================================
# Classe représentant les informations globales de l'analyse.
# ============================================================

@dataclass
class AnalysisMetadata:
    """
    Cette classe stocke les informations générales
    concernant l'analyse de l'image.
    """

    # Hauteur de l'image analysée.
    hauteur: int

    # Largeur de l'image analysée.
    largeur: int

    # Nombre total de pixels dans l'image analysée.
    nombre_total_pixels: int

    # Mode de clustering choisi.
    # Exemple : "Automatique" ou "Manuel".
    mode_clustering: str

    # Nombre final de clusters/couleurs détectées.
    nombre_clusters: int

    # Score silhouette si le mode automatique est utilisé.
    # Ce score mesure la qualité des clusters.
    score_silhouette: Optional[float]

    def to_dict(self) -> Dict[str, Any]:
        """
        Convertit l'objet en dictionnaire.
        Utile pour l'export JSON.
        """
        return asdict(self)