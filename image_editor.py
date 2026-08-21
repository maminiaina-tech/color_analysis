# image_editor.py

import numpy as np
from PIL import Image, ImageEnhance, ImageFilter, ImageOps

from constants import ARTISTIC_FILTERS, TINT_COLORS, RANDOM_STATE


# ============================================================
# Classe dédiée à la retouche d'images.
# ============================================================

class ImageEditor:
    """
    Cette classe propose des réglages inspirés de Photoshop :

    - luminosité ;
    - contraste ;
    - saturation ;
    - netteté ;
    - flou gaussien ;
    - exposition (en EV) ;
    - gamma ;
    - température (chaud / froid) ;
    - vibrance ;
    - rotation de teinte ;
    - ajustement des canaux rouge, vert, bleu ;
    - ombres et hautes lumières ;
    - noir et blanc ;
    - sépia ;
    - négatif ;
    - vignettage ;
    - postérisation, solarisation, seuil ;
    - grain de film ;
    - pixelisation (mosaïque) ;
    - teinte colorée ;
    - filtres artistiques.

    L'ordre d'application des réglages suit une logique
    proche de celle des calques de réglage dans Photoshop.
    """

    # Table de correspondance entre le nom affiché du filtre
    # artistique et le filtre PIL correspondant.
    _ARTISTIC_MAP = {
        "Contour": ImageFilter.CONTOUR,
        "Relief": ImageFilter.EMBOSS,
        "Détection de contours": ImageFilter.FIND_EDGES,
        "Lissage": ImageFilter.SMOOTH_MORE,
        "Détail": ImageFilter.DETAIL,
        "Renforcement des contours": ImageFilter.EDGE_ENHANCE_MORE,
        "Flou artistique": ImageFilter.BLUR,
    }

    # ========================================================
    # Fonction principale : application de tous les réglages.
    # ========================================================

    def apply(
        self,
        image_rgb: np.ndarray,
        brightness: float = 100.0,
        contrast: float = 100.0,
        saturation: float = 100.0,
        sharpness: float = 100.0,
        blur: float = 0.0,
        hue: float = 0.0,
        temperature: float = 0.0,
        exposure: float = 0.0,
        gamma: float = 1.0,
        vibrance: float = 0.0,
        red: float = 0.0,
        green: float = 0.0,
        blue: float = 0.0,
        grayscale: bool = False,
        sepia: bool = False,
        invert: bool = False,
        vignette: float = 0.0,
        shadows: float = 0.0,
        highlights: float = 0.0,
        posterize: int = 0,
        solarize: int = 0,
        threshold: int = 0,
        grain: float = 0.0,
        pixelate: int = 0,
        tint_color: str = "Aucune",
        tint_intensity: float = 0.0,
        artistic: str = "Aucun",
    ) -> np.ndarray:
        """
        Applique les réglages à une image RGB et retourne
        l'image retouchée.

        Paramètres :
        - image_rgb : image NumPy de forme (H, W, 3).
        - les autres paramètres sont les réglages de retouche.
        """

        # Étape 1 : conversion en image PIL.
        img = self._to_pil(image_rgb)

        # Étape 2 : filtres de base (noir et blanc, sépia).
        if grayscale:
            img = self._grayscale(img)
        if sepia:
            img = self._sepia(img)

        # Étape 3 : filtre artistique.
        if artistic != "Aucun":
            img = self._artistic(img, artistic)

        # Étape 4 : ajustement des canaux et de la température.
        arr = self._to_array(img).astype(np.float32)
        arr = self._channel_gains(arr, red, green, blue)
        arr = self._temperature(arr, temperature)
        img = self._to_pil(arr)

        # Étape 5 : rotation de teinte.
        if hue:
            img = self._hue_rotation(img, hue)

        # Étape 6 : vibrance.
        if vibrance:
            img = self._vibrance(img, vibrance)

        # Étape 7 : saturation.
        img = ImageEnhance.Color(img).enhance(saturation / 100.0)

        # Étape 8 : ombres et hautes lumières.
        arr = self._to_array(img).astype(np.float32)
        arr = self._shadows(arr, shadows)
        arr = self._highlights(arr, highlights)

        # Étape 9 : exposition et gamma.
        arr = self._exposure(arr, exposure)
        arr = self._gamma(arr, gamma)
        img = self._to_pil(arr)

        # Étape 10 : luminosité et contraste.
        img = ImageEnhance.Brightness(img).enhance(brightness / 100.0)
        img = ImageEnhance.Contrast(img).enhance(contrast / 100.0)

        # Étape 11 : netteté.
        img = ImageEnhance.Sharpness(img).enhance(sharpness / 100.0)

        # Étape 12 : flou gaussien.
        if blur > 0:
            img = img.filter(ImageFilter.GaussianBlur(radius=blur))

        # Étape 13 : grain de film.
        arr = self._to_array(img).astype(np.float32)
        arr = self._grain(arr, grain)

        # Étape 14 : postérisation, solarisation et seuil.
        arr = self._posterize(arr, posterize)
        arr = self._solarize(arr, solarize)
        arr = self._threshold(arr, threshold)

        # Étape 15 : vignettage.
        arr = self._vignette(arr, vignette)
        img = self._to_pil(arr)

        # Étape 16 : pixelisation (mosaïque).
        if pixelate > 0:
            img = self._pixelate(img, pixelate)

        # Étape 17 : teinte colorée.
        arr = self._to_array(img).astype(np.float32)
        tint_rgb = TINT_COLORS.get(tint_color)
        arr = self._tint(arr, tint_rgb, tint_intensity)

        # Étape 18 : négatif.
        if invert:
            arr = 255 - arr.astype(np.int16)

        # Étape 19 : retour de l'image retouchée.
        return np.clip(arr, 0, 255).astype(np.uint8)

    # ========================================================
    # Conversions PIL <-> NumPy.
    # ========================================================

    @staticmethod
    def _to_pil(arr) -> Image.Image:
        """
        Convertit un tableau NumPy en image PIL.
        """
        return Image.fromarray(np.asarray(arr).astype(np.uint8))

    @staticmethod
    def _to_array(img) -> np.ndarray:
        """
        Convertit une image PIL en tableau NumPy uint8.
        """
        return np.asarray(img).astype(np.uint8)

    # ========================================================
    # Filtres de base.
    # ========================================================

    def _grayscale(self, img) -> Image.Image:
        """
        Convertit l'image en noir et blanc.
        """
        gray = self._to_array(img.convert("L"))
        return self._to_pil(np.dstack([gray, gray, gray]))

    def _sepia(self, img) -> Image.Image:
        """
        Applique un filtre sépia classique.
        """
        arr = self._to_array(img).astype(np.float32)
        r, g, b = arr[..., 0], arr[..., 1], arr[..., 2]

        nr = 0.393 * r + 0.769 * g + 0.189 * b
        ng = 0.349 * r + 0.686 * g + 0.168 * b
        nb = 0.272 * r + 0.534 * g + 0.131 * b

        out = np.stack([nr, ng, nb], axis=-1)
        return self._to_pil(out)

    # ========================================================
    # Filtres artistiques.
    # ========================================================

    def _artistic(self, img: Image.Image, name: str) -> Image.Image:
        """
        Applique un filtre artistique prédéfini de PIL.
        """
        filt = self._ARTISTIC_MAP.get(name)
        if filt is None:
            return img
        return img.filter(filt)

    # ========================================================
    # Ajustement des canaux de couleur.
    # ========================================================

    @staticmethod
    def _channel_gains(
        arr: np.ndarray,
        red: float,
        green: float,
        blue: float
    ) -> np.ndarray:
        """
        Ajuste chaque canal de couleur (comme les niveaux).
        """
        gains = np.array([red, green, blue], dtype=np.float32) * 1.275
        return np.clip(arr + gains, 0, 255)

    @staticmethod
    def _temperature(arr: np.ndarray, temperature: float) -> np.ndarray:
        """
        Rend l'image plus chaude ou plus froide.
        """
        t = temperature / 100.0
        arr = arr.copy()
        arr[..., 0] += t * 45
        arr[..., 1] += t * 12
        arr[..., 2] -= t * 45
        return np.clip(arr, 0, 255)

    # ========================================================
    # Ombres et hautes lumières.
    # ========================================================

    @staticmethod
    def _luma(arr: np.ndarray) -> np.ndarray:
        """
        Calcule la luminance perceptuelle (0 à 255).
        """
        return (
            0.299 * arr[..., 0]
            + 0.587 * arr[..., 1]
            + 0.114 * arr[..., 2]
        )

    @staticmethod
    def _shadows(arr: np.ndarray, shadows: float) -> np.ndarray:
        """
        Éclaircit (valeur positive) ou assombrit (négative)
        les zones sombres de l'image.
        """
        if shadows == 0:
            return arr
        arr = arr.copy()
        luma = ImageEditor._luma(arr)
        weight = (1.0 - luma / 255.0) ** 2
        arr = arr + (shadows / 100.0) * weight[..., None] * 120
        return np.clip(arr, 0, 255)

    @staticmethod
    def _highlights(arr: np.ndarray, highlights: float) -> np.ndarray:
        """
        Éclaircit (positive) ou assombrit (négative)
        les zones claires de l'image.
        """
        if highlights == 0:
            return arr
        arr = arr.copy()
        luma = ImageEditor._luma(arr)
        weight = (luma / 255.0) ** 2
        arr = arr + (highlights / 100.0) * weight[..., None] * 120
        return np.clip(arr, 0, 255)

    # ========================================================
    # Rotation de teinte.
    # ========================================================

    def _hue_rotation(self, img: Image.Image, hue: float) -> Image.Image:
        """
        Fait pivoter la teinte de l'image.

        La teinte est traitée dans l'espace HSV fourni par PIL.
        Chaque valeur du canal H est décalée via une table de
        correspondance (LUT), avec retour à 0 après 255.
        """
        hsv = img.convert("HSV")
        h, s, v = hsv.split()

        offset = int(round(hue / 360.0 * 256)) % 256
        lut = [(i + offset) % 256 for i in range(256)]
        h = h.point(lut)

        return Image.merge("HSV", (h, s, v)).convert("RGB")

    # ========================================================
    # Vibrance.
    # ========================================================

    def _vibrance(self, img: Image.Image, vibrance: float) -> Image.Image:
        """
        Ajuste la saturation en préservant les tons déjà saturés.

        Idée :
        - vibrance positive : booste surtout les couleurs ternes ;
        - vibrance négative : réduit globalement la saturation.
        """
        hsv = np.array(img.convert("HSV"), dtype=np.float32)
        h, s, v = hsv[..., 0], hsv[..., 1], hsv[..., 2]

        vf = vibrance / 100.0
        if vf >= 0:
            s = s + vf * (255.0 - s) * 0.7
        else:
            s = s * (1.0 + vf)

        hsv[..., 1] = np.clip(s, 0, 255)
        return Image.fromarray(hsv.astype(np.uint8), "HSV").convert("RGB")

    # ========================================================
    # Exposition et gamma.
    # ========================================================

    @staticmethod
    def _exposure(arr: np.ndarray, exposure: float) -> np.ndarray:
        """
        Modifie l'exposition en valeurs d'EV.
        Chaque +1 EV double la luminosité.
        """
        return np.clip(arr * (2.0 ** exposure), 0, 255)

    @staticmethod
    def _gamma(arr: np.ndarray, gamma: float) -> np.ndarray:
        """
        Corrige le gamma de l'image.
        """
        normalized = np.clip(arr / 255.0, 0, 1)
        corrected = np.power(normalized, 1.0 / gamma) * 255.0
        return np.clip(corrected, 0, 255)

    # ========================================================
    # Grain de film.
    # ========================================================

    @staticmethod
    def _grain(arr: np.ndarray, grain: float) -> np.ndarray:
        """
        Ajoute un bruit gaussien pour imiter le grain de film.

        La graine est fixe afin que le rendu reste stable
        d'un rafraîchissement à l'autre de la page.
        """
        if grain <= 0:
            return arr
        noise = np.random.default_rng(RANDOM_STATE).normal(
            0.0,
            grain / 100.0 * 50.0,
            size=arr.shape
        )
        return np.clip(arr + noise, 0, 255)

    # ========================================================
    # Postérisation, solarisation et seuil.
    # ========================================================

    @staticmethod
    def _posterize(arr: np.ndarray, levels: int) -> np.ndarray:
        """
        Réduit le nombre de niveaux de gris par canal.
        Exemple : 4 niveaux -> effet "affiche".
        """
        if levels < 2:
            return arr
        factor = (levels - 1) / 255.0
        quantized = np.round(arr * factor) / factor
        return np.clip(quantized, 0, 255)

    @staticmethod
    def _solarize(arr: np.ndarray, threshold: float) -> np.ndarray:
        """
        Inverse les valeurs au-dessus d'un seuil (effet Sabattier).
        """
        if threshold <= 0:
            return arr
        arr = arr.astype(np.float32)
        return np.where(arr < threshold, arr, 255.0 - arr)

    @staticmethod
    def _threshold(arr: np.ndarray, threshold: float) -> np.ndarray:
        """
        Convertit l'image en noir et blanc par seuillage.
        """
        if threshold <= 0:
            return arr
        luma = ImageEditor._luma(arr.astype(np.float32))
        mask = luma >= threshold
        return np.where(
            mask[..., None],
            np.array([255.0, 255.0, 255.0]),
            np.array([0.0, 0.0, 0.0])
        )

    # ========================================================
    # Vignettage.
    # ========================================================

    @staticmethod
    def _vignette(arr: np.ndarray, vignette: float) -> np.ndarray:
        """
        Assombrit les bords de l'image.

        Principe :
        le facteur d'assombrissement augmente avec la distance
        au centre de l'image.
        """
        height, width = arr.shape[:2]
        y, x = np.mgrid[0:height, 0:width].astype(np.float32)

        dx = (x - width / 2.0) / width
        dy = (y - height / 2.0) / height

        distance = np.sqrt(dx * dx + dy * dy) / 0.7071
        distance = np.clip(distance, 0, 1)

        factor = 1.0 - (vignette / 100.0) * (distance ** 2)
        return np.clip(arr * factor[..., None], 0, 255)

    # ========================================================
    # Pixelisation (mosaïque).
    # ========================================================

    def _pixelate(self, img: Image.Image, size: int) -> Image.Image:
        """
        Réduit puis agrandit l'image avec un filtre au plus proche
        voisin pour obtenir un effet de mosaïque.
        """
        width, height = img.size
        block = max(1, int(size))
        small_w = max(1, width // block)
        small_h = max(1, height // block)

        small = img.resize((small_w, small_h), Image.Resampling.NEAREST)
        return small.resize((width, height), Image.Resampling.NEAREST)

    # ========================================================
    # Teinte colorée.
    # ========================================================

    @staticmethod
    def _tint(
        arr: np.ndarray,
        tint_rgb,
        intensity: float
    ) -> np.ndarray:
        """
        Recouvre l'image d'une teinte colorée uniforme.
        """
        if tint_rgb is None or intensity <= 0:
            return arr
        t = intensity / 100.0
        base = np.array(tint_rgb, dtype=np.float32)[None, None, :]
        return np.clip(arr * (1.0 - t) + base * t, 0, 255)
