# tests/test_image_processor.py

import io

import numpy as np
import pytest
from PIL import Image

from image_processor import ImageProcessor


# ============================================================
# Tests de l'échantillonnage des pixels.
# ============================================================

class TestSamplePixels:

    @pytest.fixture
    def processor(self):
        return ImageProcessor()

    def test_retourne_tous_les_pixels_si_assez(self, processor):
        """Sous la limite, tous les pixels sont conservés."""
        pixels = np.arange(30, dtype=np.float64).reshape(10, 3)

        result = processor.sample_pixels(pixels, max_samples=100)

        assert result is pixels

    def test_taille_echantillon_respectee(self, processor):
        """Au-delà de la limite, on retourne exactement max_samples."""
        pixels = np.zeros((500, 3), dtype=np.float64)

        result = processor.sample_pixels(pixels, max_samples=100)

        assert result.shape == (100, 3)

    def test_reproductibilite(self, processor):
        """Deux appels avec la même graine donnent le même échantillon."""
        rng = np.random.default_rng(0)
        pixels = rng.random((1000, 3))

        e1 = processor.sample_pixels(pixels, max_samples=50, random_state=42)
        e2 = processor.sample_pixels(pixels, max_samples=50, random_state=42)

        np.testing.assert_array_equal(e1, e2)

    def test_pixels_issues_de_l_original(self, processor):
        """Les pixels échantillonnés proviennent bien du tableau d'origine."""
        rng = np.random.default_rng(1)
        pixels = rng.random((200, 3))

        result = processor.sample_pixels(pixels, max_samples=20)

        for ligne in result:
            assert any((pixels == ligne).all(axis=1))


# ============================================================
# Tests de la reconstruction de l'image segmentée.
# ============================================================

class TestRebuildImageFromLabels:

    @pytest.fixture
    def processor(self):
        return ImageProcessor()

    def test_forme_reconstruite(self, processor):
        """L'image reconstruite a la forme (hauteur, largeur, 3)."""
        labels = np.array([0, 1, 1, 0])
        colors = np.array([[255, 0, 0], [0, 0, 255]], dtype=np.uint8)

        img = processor.rebuild_image_from_labels(
            labels, colors, height=2, width=2
        )

        assert img.shape == (2, 2, 3)

    def test_couleurs_associees_aux_labels(self, processor):
        """Chaque pixel prend la couleur de son cluster."""
        labels = np.array([0, 1, 1, 0])
        colors = np.array([[255, 0, 0], [0, 0, 255]], dtype=np.uint8)

        img = processor.rebuild_image_from_labels(
            labels, colors, height=2, width=2
        )

        np.testing.assert_array_equal(img[0, 0], [255, 0, 0])
        np.testing.assert_array_equal(img[0, 1], [0, 0, 255])
        np.testing.assert_array_equal(img[1, 0], [0, 0, 255])
        np.testing.assert_array_equal(img[1, 1], [255, 0, 0])


# ============================================================
# Tests du chargement d'image.
# ============================================================

class TestLoadImage:

    @pytest.fixture
    def processor(self):
        return ImageProcessor(max_size=32)

    def _image_en_bytes(self, size=(64, 48), color=(200, 30, 90)):
        img = Image.new("RGB", size, color)
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        buffer.seek(0)
        return buffer

    def test_conversion_rgb_et_dimensions(self, processor):
        """L'image chargée est un tableau RGB (H, W, 3)."""
        buffer = self._image_en_bytes(size=(16, 8))

        arr = processor.load_image(buffer)

        assert arr.shape == (8, 16, 3)
        assert arr.dtype == np.uint8

    def test_redimensionnement_max_size(self, processor):
        """Une grande image est réduite à max_size en gardant le ratio."""
        buffer = self._image_en_bytes(size=(300, 150))

        arr = processor.load_image(buffer)

        hauteur, largeur, _ = arr.shape
        assert max(hauteur, largeur) <= 32
        # Ratio largeur / hauteur conservé.
        assert abs(largeur / hauteur - 2.0) < 0.2

    def test_petite_image_non_agrandie(self, processor):
        """Une petite image n'est pas agrandie par thumbnail."""
        buffer = self._image_en_bytes(size=(10, 10))

        arr = processor.load_image(buffer)

        assert arr.shape == (10, 10, 3)

    def test_conversion_rgba_vers_rgb(self, processor):
        """Une image avec canal alpha est convertie en RGB."""
        img = Image.new("RGBA", (8, 8), (10, 20, 30, 255))
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        buffer.seek(0)

        arr = processor.load_image(buffer)

        assert arr.shape == (8, 8, 3)
