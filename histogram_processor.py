# histogram_processor.py

import numpy as np
import pandas as pd


# ============================================================
# Paramètres de l'histogramme de luminance.
# ============================================================

# Nombre de tranches de l'histogramme.
HISTOGRAM_BINS = 64

# Limites (valeurs de luminance 0-255) séparant les zones tonales.
SHADOWS_MAX = 85
HIGHLIGHTS_MIN = 170

# Zones tonales affichées en arrière-plan du graphique.
ZONES = [
    {"nom": "Ombres", "debut": 0.0, "fin": SHADOWS_MAX},
    {"nom": "Tons moyens", "debut": SHADOWS_MAX, "fin": HIGHLIGHTS_MIN},
    {"nom": "Hautes lumières", "debut": HIGHLIGHTS_MIN, "fin": 256.0},
]


# ============================================================
# Classe dédiée au calcul des histogrammes de luminance.
# ============================================================

class HistogramProcessor:
    """
    Cette classe calcule l'histogramme de luminance d'une image
    ainsi que des statistiques tonales (luminance moyenne,
    étalement des tons, répartition ombres / tons moyens /
    hautes lumières).

    Elle permet de comparer deux versions d'une même image
    (originale et retouchée) pour visualiser l'effet des
    réglages de retouche.
    """

    def __init__(self, bins: int = HISTOGRAM_BINS):
        """
        Constructeur de la classe.

        Paramètre :
        - bins : nombre de tranches de l'histogramme.
        """
        self.bins = bins

    # ========================================================
    # Luminance perceptuelle.
    # ========================================================

    @staticmethod
    def luminance(image_rgb: np.ndarray) -> np.ndarray:
        """
        Calcule la luminance perceptuelle de chaque pixel (0-255).

        La luminance est une moyenne pondérée des canaux RGB,
        proche de la perception humaine de la brillance.
        """
        arr = image_rgb.astype(np.float32)
        return (
            0.299 * arr[..., 0]
            + 0.587 * arr[..., 1]
            + 0.114 * arr[..., 2]
        )

    # ========================================================
    # Histogramme d'une seule image.
    # ========================================================

    def histogram(self, image_rgb: np.ndarray) -> pd.DataFrame:
        """
        Retourne un DataFrame avec une ligne par tranche de luminance :
        - valeur : centre de la tranche (axe horizontal) ;
        - debut / fin : bornes de la tranche ;
        - frequence : nombre de pixels dans la tranche.
        """
        luma = self.luminance(image_rgb)
        counts, edges = np.histogram(
            luma,
            bins=self.bins,
            range=(0, 255)
        )
        centres = (edges[:-1] + edges[1:]) / 2.0
        return pd.DataFrame(
            {
                "valeur": centres,
                "debut": edges[:-1],
                "fin": edges[1:],
                "frequence": counts,
            }
        )

    # ========================================================
    # Histogrammes des canaux de couleur.
    # ========================================================

    def channel_histogram(self, image_rgb: np.ndarray) -> pd.DataFrame:
        """
        Retourne l'histogramme de chaque canal (Rouge, Vert, Bleu)
        dans un même tableau :
        - valeur : centre de la tranche ;
        - frequence : nombre de pixels dans la tranche ;
        - canal : nom du canal ("Rouge", "Vert" ou "Bleu").
        """
        arr = image_rgb.astype(np.float32)
        frames = []

        for canal, index in [("Rouge", 0), ("Vert", 1), ("Bleu", 2)]:
            counts, edges = np.histogram(
                arr[..., index],
                bins=self.bins,
                range=(0, 255)
            )
            centres = (edges[:-1] + edges[1:]) / 2.0
            frames.append(
                pd.DataFrame(
                    {
                        "valeur": centres,
                        "frequence": counts,
                        "canal": canal,
                    }
                )
            )

        return pd.concat(frames, ignore_index=True)

    # ========================================================
    # Histogrammes comparés avant / après.
    # ========================================================

    def compare(
        self,
        avant: np.ndarray,
        apres: np.ndarray
    ) -> pd.DataFrame:
        """
        Combine les histogrammes avant / après dans un même tableau.

        Paramètres :
        - avant : image originale ;
        - apres : image retouchée.
        """
        df_avant = self.histogram(avant)
        df_avant["image"] = "Originale"

        df_apres = self.histogram(apres)
        df_apres["image"] = "Retouchée"

        return pd.concat([df_avant, df_apres], ignore_index=True)

    # ========================================================
    # Statistiques tonales d'une image.
    # ========================================================

    @staticmethod
    def statistiques(image_rgb: np.ndarray) -> dict:
        """
        Calcule les statistiques tonales d'une image :
        - moyenne / mediane : luminosité moyenne et médiane (0-255) ;
        - ecart_type : étalement des tons (indicateur de contraste) ;
        - min / max : luminance minimale et maximale ;
        - ombres / tons_moyens / hautes_lumieres : pourcentages
          de pixels dans chaque zone tonale ;
        - canaux : moyenne, médiane et écart-type de chaque canal
          Rouge / Vert / Bleu.
        """
        luma = HistogramProcessor.luminance(image_rgb)
        arr = image_rgb.astype(np.float32)

        ombres = float(np.mean(luma < SHADOWS_MAX)) * 100.0
        hautes = float(np.mean(luma >= HIGHLIGHTS_MIN)) * 100.0

        def stats_canal(channel: np.ndarray) -> dict:
            return {
                "moyenne": round(float(np.mean(channel)), 1),
                "mediane": round(float(np.median(channel)), 1),
                "ecart_type": round(float(np.std(channel)), 1),
            }

        return {
            "moyenne": round(float(np.mean(luma)), 1),
            "mediane": round(float(np.median(luma)), 1),
            "ecart_type": round(float(np.std(luma)), 1),
            "min": round(float(np.min(luma)), 1),
            "max": round(float(np.max(luma)), 1),
            "ombres": round(ombres, 1),
            "tons_moyens": round(100.0 - ombres - hautes, 1),
            "hautes_lumieres": round(hautes, 1),
            "canaux": {
                "Rouge": stats_canal(arr[..., 0]),
                "Vert": stats_canal(arr[..., 1]),
                "Bleu": stats_canal(arr[..., 2]),
            },
        }
