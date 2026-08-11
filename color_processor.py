from functools import cached_property
from typing import Optional

import numpy as np
from skimage.color import rgb2lab, lab2rgb

from constants import REFERENCE_COLORS


# ============================================================
# Classe dédiée au traitement des couleurs.
# ============================================================

class ColorProcessor:
    """
    Cette classe s'occupe :
    - de la conversion RGB vers LAB ;
    - de la conversion LAB vers RGB ;
    - de la conversion RGB vers HEX ;
    - du nommage approximatif des couleurs.
    """

    def __init__(self, reference_colors: Optional[dict] = None):
        """
        Constructeur de la classe.

        Paramètres :
        - reference_colors : dictionnaire des couleurs de référence.
          Si aucune valeur n'est donnée, on utilise REFERENCE_COLORS.
        """

        # Couleurs utilisées pour nommer les couleurs dominantes.
        self.reference_colors = reference_colors or REFERENCE_COLORS

    # ========================================================
    # Conversion des couleurs de référence vers LAB.
    # ========================================================

    @cached_property
    def reference_lab(self) -> np.ndarray:
        """
        Cette propriété convertit les couleurs de référence
        depuis RGB vers LAB.

        Pourquoi LAB ?
        - LAB est plus proche de la perception humaine.
        - Les distances dans LAB sont plus significatives
          que les distances dans RGB.
        """

        # Étape 1 : récupérer les valeurs RGB des couleurs
        # de référence sous forme de tableau NumPy.
        ref_rgb = np.array(
            list(self.reference_colors.values()),
            dtype=np.float64
        ) / 255.0

        # Étape 2 : reshape sous forme d'une petite image.
        # scikit-image attend une image de forme (H, W, 3).
        ref_rgb_img = ref_rgb.reshape(1, -1, 3)

        # Étape 3 : conversion RGB -> LAB.
        ref_lab = rgb2lab(ref_rgb_img)

        # Étape 4 : reshape pour obtenir une liste de couleurs.
        # Résultat : forme (nombre_de_couleurs, 3)
        return ref_lab.reshape(-1, 3)

    # ========================================================
    # Conversion d'une image RGB vers LAB.
    # ========================================================

    def rgb_image_to_lab(self, image_rgb: np.ndarray) -> np.ndarray:
        """
        Cette fonction convertit une image RGB en image LAB.

        Étapes :
        1. Normaliser les pixels entre 0 et 1.
        2. Convertir l'image RGB vers LAB.
        3. Retourner l'image LAB.
        """

        # Étape 1 : normalisation.
        # Les pixels RGB sont généralement entre 0 et 255.
        # scikit-image attend souvent des valeurs entre 0 et 1.
        image_float = image_rgb.astype(np.float64) / 255.0

        # Étape 2 : conversion RGB -> LAB.
        image_lab = rgb2lab(image_float)

        # Étape 3 : retour de l'image LAB.
        return image_lab

    # ========================================================
    # Conversion des centres LAB vers RGB.
    # ========================================================

    def lab_centers_to_rgb(self, centers_lab: np.ndarray) -> np.ndarray:
        """
        Cette fonction convertit les centres des clusters,
        obtenus dans l'espace LAB, vers RGB.

        Étapes :
        1. Reshape des centres LAB pour scikit-image.
        2. Conversion LAB -> RGB.
        3. Mise à l'échelle entre 0 et 255.
        4. Bornage des valeurs entre 0 et 255.
        """

        # Étape 1 : reshape.
        # scikit-image attend une image de forme (H, W, 3).
        centers_lab_img = centers_lab.reshape(1, -1, 3)

        # Étape 2 : conversion LAB -> RGB.
        # La sortie est généralement entre 0 et 1.
        centers_rgb_float = lab2rgb(centers_lab_img).reshape(-1, 3)

        # Étape 3 : passage de [0, 1] vers [0, 255].
        centers_rgb = centers_rgb_float * 255

        # Étape 4 : clip et conversion en entiers.
        # Certaines valeurs peuvent légèrement dépasser 255
        # à cause de conversions colorimétriques.
        centers_rgb = np.clip(centers_rgb, 0, 255).astype(np.uint8)

        return centers_rgb

    # ========================================================
    # Conversion RGB vers HEX.
    # ========================================================

    def rgb_to_hex(self, rgb) -> str:
        """
        Cette fonction convertit une couleur RGB en code HEX.

        Exemple :
        (255, 0, 0) -> #ff0000
        """

        # Conversion des composantes en entiers.
        r = int(rgb[0])
        g = int(rgb[1])
        b = int(rgb[2])

        # Formatage en hexadécimal.
        return "#{:02x}{:02x}{:02x}".format(r, g, b)

    # ========================================================
    # Nommage approximatif d'une couleur.
    # ========================================================

    def get_color_name(self, center_lab: np.ndarray):
        """
        Cette fonction associe une couleur extraite à la couleur
        de référence la plus proche dans l'espace LAB.

        Étapes :
        1. Calculer la distance entre la couleur extraite
           et toutes les couleurs de référence.
        2. Trouver l'indice de la distance minimale.
        3. Retourner le nom de la couleur et la distance.
        """

        # Étape 1 : calcul des distances euclidiennes
        # entre la couleur dominante et les couleurs de référence.
        distances = np.linalg.norm(
            self.reference_lab - center_lab,
            axis=1
        )

        # Étape 2 : indice de la couleur de référence la plus proche.
        idx = int(np.argmin(distances))

        # Étape 3 : récupération du nom.
        name = list(self.reference_colors.keys())[idx]

        # Distance minimale, utile pour mesurer la confiance.
        distance = float(distances[idx])

        return name, distance