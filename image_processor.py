from PIL import Image
import numpy as np

from constants import DEFAULT_MAX_SIZE, RANDOM_STATE


# ============================================================
# Classe dédiée au traitement de base de l'image.
# ============================================================

class ImageProcessor:
    """
    Cette classe s'occupe :
    - du chargement de l'image ;
    - du redimensionnement ;
    - de l'échantillonnage des pixels ;
    - de la reconstruction de l'image segmentée.
    """

    def __init__(self, max_size: int = DEFAULT_MAX_SIZE):
        """
        Constructeur de la classe.

        Paramètres :
        - max_size : taille maximale de l'image après redimensionnement.
        """

        # Taille maximale utilisée pour limiter le temps de calcul.
        self.max_size = max_size

    # ========================================================
    # Chargement de l'image uploadée.
    # ========================================================

    def load_image(self, uploaded_file) -> np.ndarray:
        """
        Cette fonction lit l'image uploadée par l'utilisateur.

        Étapes :
        1. Ouvrir l'image depuis le fichier uploadé.
        2. Convertir l'image en RGB.
        3. Redimensionner l'image pour accélérer le traitement.
        4. Retourner l'image sous forme de tableau NumPy.
        """

        # Étape 1 : ouverture de l'image.
        img = Image.open(uploaded_file)

        # Étape 2 : conversion en RGB.
        # Cela permet d'avoir toujours 3 canaux : R, G, B.
        img = img.convert("RGB")

        # Étape 3 : redimensionnement.
        # thumbnail conserve le ratio de l'image.
        img.thumbnail((self.max_size, self.max_size))

        # Étape 4 : conversion en tableau NumPy.
        # Le tableau aura la forme : (hauteur, largeur, 3)
        return np.array(img)

    # ========================================================
    # Échantillonnage des pixels.
    # ========================================================

    def sample_pixels(
        self,
        pixels: np.ndarray,
        max_samples: int,
        random_state: int = RANDOM_STATE
    ) -> np.ndarray:
        """
        Cette fonction sélectionne un sous-ensemble de pixels.

        Objectif :
        - accélérer le clustering ;
        - réduire la mémoire utilisée ;
        - conserver une représentation globale des couleurs.

        Étapes :
        1. Vérifier si le nombre de pixels est trop élevé.
        2. Si oui, tirer aléatoirement un échantillon.
        3. Retourner l'échantillon.
        """

        # Étape 1 : si le nombre de pixels est acceptable,
        # on retourne directement tous les pixels.
        if len(pixels) <= max_samples:
            return pixels

        # Étape 2 : création d'un générateur aléatoire.
        rng = np.random.default_rng(random_state)

        # Sélection aléatoire d'indices sans remise.
        indices = rng.choice(
            len(pixels),
            size=max_samples,
            replace=False
        )

        # Étape 3 : retour des pixels échantillonnés.
        return pixels[indices]

    # ========================================================
    # Reconstruction de l'image segmentée.
    # ========================================================

    def rebuild_image_from_labels(
        self,
        labels: np.ndarray,
        colors: np.ndarray,
        height: int,
        width: int
    ) -> np.ndarray:
        """
        Cette fonction reconstruit une image segmentée.

        Principe :
        Chaque pixel est remplacé par la couleur du cluster
        auquel il appartient.

        Étapes :
        1. Prendre le label de chaque pixel.
        2. Remplacer chaque label par la couleur du centre.
        3. Remodeler le tableau pour retrouver la taille
           de l'image originale.
        """

        # Étape 1 et 2 :
        # labels contient l'index du cluster de chaque pixel.
        # colors contient les couleurs RGB des centres de clusters.
        segmented_pixels = colors[labels]

        # Étape 3 :
        # On redonne à l'image sa forme : hauteur x largeur x 3.
        return segmented_pixels.reshape(height, width, 3)