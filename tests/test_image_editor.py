# tests/test_image_editor.py

import numpy as np
import pytest

from image_editor import ImageEditor


# ============================================================
# Tests de la fonction principale apply().
# ============================================================

class TestApply:

    @pytest.fixture
    def editor(self):
        return ImageEditor()

    def test_reglages_par_defaut_image_inchangee(self, editor, image_degradee):
        """Sans aucun réglage, l'image de sortie est identique."""
        result = editor.apply(image_degradee)

        np.testing.assert_array_equal(result, image_degradee)

    def test_forme_conservee(self, editor, image_degradee):
        result = editor.apply(
            image_degradee,
            brightness=120,
            contrast=80,
            saturation=150,
            blur=2.0,
            pixelate=4,
            vignette=50,
        )

        assert result.shape == image_degradee.shape
        assert result.dtype == np.uint8

    def test_negatif(self, editor, image_degradee):
        """Le négatif inverse chaque canal : sortie = 255 - entrée."""
        result = editor.apply(image_degradee, invert=True)

        np.testing.assert_array_equal(result, 255 - image_degradee)

    def test_noir_et_blanc_canaux_identiques(self, editor, image_degradee):
        """En N&B, les trois canaux sont égaux."""
        result = editor.apply(image_degradee, grayscale=True)

        np.testing.assert_array_equal(
            result[..., 0], result[..., 1]
        )
        np.testing.assert_array_equal(
            result[..., 1], result[..., 2]
        )

    def test_seuil_noir_et_blanc(self, editor):
        """Avec threshold, seules des valeurs pures 0/255 sortent."""
        img = np.full((4, 4, 3), 128, dtype=np.uint8)

        result = editor.apply(img, threshold=100)

        assert set(np.unique(result)).issubset({0, 255})

    def test_exposition_double_la_luminosite(self, editor):
        """+1 EV double la luminosité (avec clipping à 255)."""
        img = np.full((2, 2, 3), 50, dtype=np.uint8)

        result = editor.apply(img, exposure=1.0)

        np.testing.assert_array_equal(result, np.full((2, 2, 3), 100, dtype=np.uint8))

    def test_gamma_un_nechange_rien(self, editor, image_degradee):
        result = editor.apply(image_degradee, gamma=1.0)

        np.testing.assert_array_equal(result, image_degradee)

    def test_pixelisation_conserve_dimensions(self, editor, image_degradee):
        result = editor.apply(image_degradee, pixelate=5)

        assert result.shape == image_degradee.shape

    def test_teinte_colorée_melange(self, editor, image_rouge):
        """
        Une teinte rouge à 100 % donne exactement la couleur
        de teinte sur toute l'image.
        """
        result = editor.apply(
            image_rouge,
            tint_color="Bleu",
            tint_intensity=100.0,
        )

        np.testing.assert_array_equal(result, np.full((4, 4, 3), (0, 0, 255), dtype=np.uint8))

    def test_posterisation_reduit_les_niveaux(self, editor, image_degradee):
        """La postérisation réduit le nombre de valeurs uniques."""
        avant = len(np.unique(image_degradee))
        apres = editor.apply(image_degradee, posterize=2)

        assert len(np.unique(apres)) < avant


# ============================================================
# Tests des fonctions internes.
# ============================================================

class TestFonctionsInternes:

    @pytest.fixture
    def editor(self):
        return ImageEditor()

    def test_channel_gains_augmente_le_rouge(self):
        arr = np.full((1, 1, 3), 100.0, dtype=np.float32)

        out = ImageEditor._channel_gains(arr, red=10, green=0, blue=0)

        assert out[0, 0, 0] == pytest.approx(112.75)
        assert out[0, 0, 1] == pytest.approx(100.0)

    def test_temperature_chauffe(self):
        """Température positive : +rouge, -bleu."""
        arr = np.full((1, 1, 3), 128.0, dtype=np.float32)

        out = ImageEditor._temperature(arr, temperature=100)

        assert out[0, 0, 0] > 128
        assert out[0, 0, 2] < 128

    def test_exposition_clipping_a_255(self):
        arr = np.full((1, 1, 3), 200.0, dtype=np.float32)

        out = ImageEditor._exposure(arr, exposure=2.0)

        assert np.all(out == 255)

    def test_vignette_assombrit_les_bords(self, editor):
        """Les coins sont plus sombres que le centre."""
        arr = np.full((20, 20, 3), 200.0, dtype=np.float32)

        out = ImageEditor._vignette(arr, vignette=80)

        centre = out[10, 10]
        coin = out[0, 0]
        assert coin.mean() < centre.mean()

    def test_grain_zero_nechange_rien(self, editor, image_degradee):
        arr = image_degradee.astype(np.float32)

        out = ImageEditor._grain(arr, grain=0)

        np.testing.assert_array_equal(out, arr)

    def test_solarize_inverse_au_dela_du_seuil(self):
        arr = np.array([[[100.0, 200.0, 250.0]]], dtype=np.float32)

        out = ImageEditor._solarize(arr, threshold=180)

        # 100 < 180 : inchangé ; 200 et 250 : inversés.
        assert out[0, 0, 0] == pytest.approx(100.0)
        assert out[0, 0, 1] == pytest.approx(55.0)
        assert out[0, 0, 2] == pytest.approx(5.0)

    def test_sepia_sortie_dans_les_limites(self, editor, image_blanche):
        """Le sépia du blanc reste dans [0, 255]."""
        result = editor.apply(image_blanche, sepia=True)

        assert result.min() >= 0
        assert result.max() <= 255

    def test_hue_rotation_change_les_couleurs(self, editor, image_rouge):
        """Une rotation de 180° transforme le rouge en cyan."""
        result = editor.apply(image_rouge, hue=180)

        # Cyan : canal rouge faible, bleu/vert élevés.
        assert result[..., 0].mean() < 100
        assert result[..., 2].mean() > 150
