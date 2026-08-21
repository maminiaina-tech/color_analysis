# tests/test_color_processor.py

import numpy as np
import pytest

from color_processor import ColorProcessor


# ============================================================
# Tests de la conversion RGB -> HEX.
# ============================================================

class TestRgbToHex:

    @pytest.fixture
    def processor(self):
        return ColorProcessor()

    def test_rouge_pur(self, processor):
        assert processor.rgb_to_hex((255, 0, 0)) == "#ff0000"

    def test_blanc(self, processor):
        assert processor.rgb_to_hex((255, 255, 255)) == "#ffffff"

    def test_noir(self, processor):
        assert processor.rgb_to_hex((0, 0, 0)) == "#000000"

    def test_padding_deux_chiffres(self, processor):
        """Les valeurs faibles sont complétées par un zéro."""
        assert processor.rgb_to_hex((1, 2, 3)) == "#010203"

    def test_accepte_tableau_numpy(self, processor):
        arr = np.array([18, 52, 86], dtype=np.uint8)
        assert processor.rgb_to_hex(arr) == "#123456"


# ============================================================
# Tests de la conversion RGB -> LAB.
# ============================================================

class TestRgbImageToLab:

    @pytest.fixture
    def processor(self):
        return ColorProcessor()

    def test_forme_conservee(self, processor, image_degradee):
        """La conversion ne change pas les dimensions."""
        lab = processor.rgb_image_to_lab(image_degradee)

        assert lab.shape == image_degradee.shape

    def test_noir_a_l_zero(self, processor, image_noire):
        """Le noir pur a une luminance LAB de 0."""
        lab = processor.rgb_image_to_lab(image_noire)

        assert np.allclose(lab[..., 0], 0.0, atol=0.5)

    def test_blanc_a_l_cent(self, processor, image_blanche):
        """Le blanc pur a une luminance LAB de 100."""
        lab = processor.rgb_image_to_lab(image_blanche)

        assert np.allclose(lab[..., 0], 100.0, atol=0.5)


# ============================================================
# Tests de la conversion des centres LAB -> RGB.
# ============================================================

class TestLabCentersToRgb:

    @pytest.fixture
    def processor(self):
        return ColorProcessor()

    def test_valeurs_dans_les_limites(self, processor):
        """Les valeurs RGB restent entre 0 et 255."""
        centers_lab = np.array([[50.0, 60.0, 40.0], [25.0, -20.0, 30.0]])

        centers_rgb = processor.lab_centers_to_rgb(centers_lab)

        assert centers_rgb.dtype == np.uint8
        assert centers_rgb.min() >= 0
        assert centers_rgb.max() <= 255

    def test_aller_retour_rouge(self, processor):
        """
        Un centre correspondant au rouge pur doit donner
        un RGB proche du rouge après conversion.
        """
        rouge_lab = np.array([[53.24, 80.09, 67.20]])

        rgb = processor.lab_centers_to_rgb(rouge_lab)[0]

        assert abs(int(rgb[0]) - 255) <= 2
        assert int(rgb[1]) <= 2
        assert int(rgb[2]) <= 2


# ============================================================
# Tests du nommage approximatif des couleurs.
# ============================================================

class TestGetColorName:

    @pytest.fixture
    def processor(self):
        return ColorProcessor()

    def test_nomme_le_rouge(self, processor):
        """Une couleur proche du rouge de référence est nommée rouge."""
        rouge_lab = processor.reference_lab[
            list(processor.reference_colors).index("rouge")
        ]

        name, distance = processor.get_color_name(rouge_lab)

        assert name == "rouge"
        assert distance == pytest.approx(0.0, abs=1e-6)

    def test_distance_positive(self, processor):
        """La distance retournée est toujours positive ou nulle."""
        center = np.array([50.0, 10.0, -10.0])

        _, distance = processor.get_color_name(center)

        assert distance >= 0.0

    def test_reference_lab_forme_coherente(self, processor):
        """reference_lab a autant de lignes que de couleurs."""
        nb_couleurs = len(processor.reference_colors)

        assert processor.reference_lab.shape == (nb_couleurs, 3)

    def test_couleurs_personnalisees(self):
        """On peut fournir son propre dictionnaire de couleurs."""
        custom = {"ma_couleur": (10, 200, 10)}
        processor = ColorProcessor(reference_colors=custom)

        # LAB du vert vif : on récupère via la conversion inverse.
        lab = processor.rgb_image_to_lab(
            np.full((1, 1, 3), (10, 200, 10), dtype=np.uint8)
        )[0, 0]

        name, distance = processor.get_color_name(lab)

        assert name == "ma_couleur"
        assert distance == pytest.approx(0.0, abs=1.0)
