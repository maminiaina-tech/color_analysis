# tests/test_histogram_processor.py

import numpy as np
import pandas as pd
import pytest

from histogram_processor import (
    HistogramProcessor,
    HISTOGRAM_BINS,
    SHADOWS_MAX,
    HIGHLIGHTS_MIN,
)


# ============================================================
# Tests de la luminance perceptuelle.
# ============================================================

class TestLuminance:

    def test_noir_vaut_zero(self, image_noire):
        luma = HistogramProcessor.luminance(image_noire)

        assert np.all(luma == 0)

    def test_blanc_vaut_255(self, image_blanche):
        luma = HistogramProcessor.luminance(image_blanche)

        assert np.allclose(luma, 255.0)

    def test_gris_moyen(self):
        """Un gris uniforme (128 partout) donne ~128."""
        img = np.full((2, 2, 3), 128, dtype=np.uint8)

        luma = HistogramProcessor.luminance(img)

        assert np.allclose(luma, 128.0)

    def test_forme_sans_canal_couleur(self, image_degradee):
        """La luminance est un tableau 2D (H, W)."""
        luma = HistogramProcessor.luminance(image_degradee)

        assert luma.shape == image_degradee.shape[:2]

    def test_formule_ponderee(self):
        """Vérifie la formule 0.299 R + 0.587 G + 0.114 B."""
        img = np.array([[[100, 150, 200]]], dtype=np.uint8)
        attendu = 0.299 * 100 + 0.587 * 150 + 0.114 * 200

        luma = HistogramProcessor.luminance(img)

        assert luma[0, 0] == pytest.approx(attendu)


# ============================================================
# Tests de l'histogramme de luminance.
# ============================================================

class TestHistogram:

    @pytest.fixture
    def processor(self):
        return HistogramProcessor()

    def test_nombre_de_lignes(self, processor, image_degradee):
        df = processor.histogram(image_degradee)

        assert len(df) == HISTOGRAM_BINS

    def test_colonnes_attendues(self, processor, image_degradee):
        df = processor.histogram(image_degradee)

        assert list(df.columns) == ["valeur", "debut", "fin", "frequence"]

    def test_frequences_somment_au_total(self, processor, image_degradee):
        """Tous les pixels sont comptés une fois."""
        df = processor.histogram(image_degradee)

        assert df["frequence"].sum() == image_degradee.shape[0] * image_degradee.shape[1]

    def test_image_uniforme_concentree(self, processor, image_rouge):
        """
        Une image uniforme place tous ses pixels dans la tranche
        contenant sa luminance (~54 pour le rouge pur).
        """
        df = processor.histogram(image_rouge)

        idx_max = df["frequence"].idxmax()
        centre = df.loc[idx_max, "valeur"]

        # Luminance du rouge pur : 0.299 * 255 ≈ 76.
        assert abs(centre - 76.2) < 255 / HISTOGRAM_BINS


# ============================================================
# Tests des histogrammes par canal.
# ============================================================

class TestChannelHistogram:

    @pytest.fixture
    def processor(self):
        return HistogramProcessor()

    def test_trois_canaux_presents(self, processor, image_degradee):
        df = processor.channel_histogram(image_degradee)

        assert set(df["canal"].unique()) == {"Rouge", "Vert", "Bleu"}

    def test_taille_totale(self, processor, image_degradee):
        """3 canaux x bins lignes."""
        df = processor.channel_histogram(image_degradee)

        assert len(df) == 3 * HISTOGRAM_BINS

    def test_chaque_canal_compte_tous_les_pixels(
        self, processor, image_degradee
    ):
        df = processor.channel_histogram(image_degradee)
        total_pixels = image_degradee.shape[0] * image_degradee.shape[1]

        for canal in ["Rouge", "Vert", "Bleu"]:
            freq = df[df["canal"] == canal]["frequence"].sum()
            assert freq == total_pixels


# ============================================================
# Tests de la comparaison avant / après.
# ============================================================

class TestCompare:

    @pytest.fixture
    def processor(self):
        return HistogramProcessor()

    def test_deux_images_concatenees(self, processor, image_rouge, image_bleue=None):
        img_apres = np.full((4, 4, 3), (0, 0, 255), dtype=np.uint8)

        df = processor.compare(image_rouge, img_apres)

        assert len(df) == 2 * HISTOGRAM_BINS
        assert set(df["image"].unique()) == {"Originale", "Retouchée"}


# ============================================================
# Tests des statistiques tonales.
# ============================================================

class TestStatistiques:

    def test_image_noire(self, image_noire):
        stats = HistogramProcessor.statistiques(image_noire)

        assert stats["moyenne"] == 0.0
        assert stats["min"] == 0.0
        assert stats["max"] == 0.0
        assert stats["ombres"] == 100.0
        assert stats["hautes_lumieres"] == 0.0

    def test_image_blanche(self, image_blanche):
        stats = HistogramProcessor.statistiques(image_blanche)

        assert stats["moyenne"] == 255.0
        assert stats["hautes_lumieres"] == 100.0
        assert stats["ombres"] == 0.0

    def test_zones_tonales_somment_a_cent(self, image_degradee):
        stats = HistogramProcessor.statistiques(image_degradee)

        total = (
            stats["ombres"]
            + stats["tons_moyens"]
            + stats["hautes_lumieres"]
        )
        assert total == pytest.approx(100.0, abs=0.3)

    def test_statistiques_par_canal(self, image_degradee):
        stats = HistogramProcessor.statistiques(image_degradee)

        for canal in ["Rouge", "Vert", "Bleu"]:
            assert set(stats["canaux"][canal].keys()) == {
                "moyenne", "mediane", "ecart_type"
            }

    def test_moyenne_canal_coherente(self, image_degradee):
        """La moyenne du canal Rouge correspond à NumPy."""
        stats = HistogramProcessor.statistiques(image_degradee)
        attendu = round(float(np.mean(image_degradee[..., 0])), 1)

        assert stats["canaux"]["Rouge"]["moyenne"] == attendu

    def test_seuils_coherents_avec_constantes(self):
        """Les seuils utilisés correspondent aux constantes."""
        assert SHADOWS_MAX < HIGHLIGHTS_MIN
