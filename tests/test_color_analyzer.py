# tests/test_color_analyzer.py

import numpy as np
import pytest

from color_analyzer import ColorAnalyzer
from models import ColorResult, AnalysisMetadata


# ============================================================
# Tests du pipeline complet d'analyse.
# ============================================================

class TestAnalyze:

    @pytest.fixture
    def analyzer(self):
        return ColorAnalyzer()

    def test_retourne_trois_resultats(self, analyzer, image_bicolore):
        """analyze retourne (couleurs, image_segmentee, metadata)."""
        result = analyzer.analyze(image_bicolore, mode="Manuel", fixed_k=2)

        assert len(result) == 3

    def test_deux_couleurs_detectees(self, analyzer, image_bicolore):
        """Une image bicolore donne exactement 2 couleurs dominantes."""
        couleurs, _, _ = analyzer.analyze(
            image_bicolore, mode="Manuel", fixed_k=2
        )

        assert len(couleurs) == 2
        assert all(isinstance(c, ColorResult) for c in couleurs)

    def test_proportions_triees_decroissantes(self, analyzer, image_bicolore):
        """Les couleurs sont triées par proportion décroissante."""
        couleurs, _, _ = analyzer.analyze(
            image_bicolore, mode="Manuel", fixed_k=2
        )

        proportions = [c.proportion for c in couleurs]
        assert proportions == sorted(proportions, reverse=True)

    def test_somme_des_proportions_egale_un(self, analyzer, image_bicolore):
        """La somme des proportions vaut environ 1."""
        couleurs, _, _ = analyzer.analyze(
            image_bicolore, mode="Manuel", fixed_k=2
        )

        assert sum(c.proportion for c in couleurs) == pytest.approx(1.0)

    def test_image_segmentee_meme_forme(self, analyzer, image_bicolore):
        """L'image segmentée garde les dimensions de l'originale."""
        _, segmentee, _ = analyzer.analyze(
            image_bicolore, mode="Manuel", fixed_k=2
        )

        assert segmentee.shape == image_bicolore.shape

    def test_metadata_coherente(self, analyzer, image_bicolore):
        """Les métadonnées décrivent correctement l'analyse."""
        _, _, metadata = analyzer.analyze(
            image_bicolore, mode="Manuel", fixed_k=3
        )

        assert isinstance(metadata, AnalysisMetadata)
        assert metadata.hauteur == 2
        assert metadata.largeur == 2
        assert metadata.nombre_total_pixels == 4
        assert metadata.mode_clustering == "Manuel"
        assert metadata.nombre_clusters == 3
        # Mode manuel : pas de score silhouette.
        assert metadata.score_silhouette is None

    def test_mode_automatique_calcule_le_score(self, analyzer, image_bicolore):
        """Le mode automatique renseigne le score silhouette."""
        _, _, metadata = analyzer.analyze(image_bicolore, mode="Automatique")

        assert metadata.score_silhouette is not None
        assert -1.0 <= metadata.score_silhouette <= 1.0

    def test_codes_hex_valides(self, analyzer, image_bicolore):
        """Chaque couleur possède un code HEX bien formé."""
        couleurs, _, _ = analyzer.analyze(
            image_bicolore, mode="Manuel", fixed_k=2
        )

        for couleur in couleurs:
            assert couleur.hex.startswith("#")
            assert len(couleur.hex) == 7
            int(couleur.hex[1:], 16)  # lève une erreur si invalide

    def test_rangs_sequentiels(self, analyzer, image_bicolore):
        """Les rangs commencent à 1 et s'incrémentent."""
        couleurs, _, _ = analyzer.analyze(
            image_bicolore, mode="Manuel", fixed_k=2
        )

        assert [c.rang for c in couleurs] == [1, 2]

    def test_image_monochrome(self, analyzer, image_rouge):
        """
        Une image uniforme produit des clusters dont les couleurs
        sont toutes proches du rouge.
        """
        couleurs, segmentee, _ = analyzer.analyze(
            image_rouge, mode="Manuel", fixed_k=2
        )

        # Tous les pixels segmentés restent rougeâtres.
        assert segmentee[..., 0].mean() > 200
        assert segmentee[..., 1].mean() < 100
