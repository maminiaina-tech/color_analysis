# tests/test_models.py

import pytest

from models import ColorResult, AnalysisMetadata


# ============================================================
# Tests de la classe ColorResult.
# ============================================================

class TestColorResult:

    def test_creation_attributs(self):
        """Les attributs sont bien stockés à la création."""
        result = ColorResult(
            rang=1,
            nom="rouge",
            rgb=[255, 0, 0],
            hex="#ff0000",
            pixels=100,
            proportion=0.5,
            proportion_pct=50.0,
            distance_lab=1.23,
        )

        assert result.rang == 1
        assert result.nom == "rouge"
        assert result.rgb == [255, 0, 0]
        assert result.hex == "#ff0000"
        assert result.pixels == 100
        assert result.proportion == 0.5
        assert result.proportion_pct == 50.0
        assert result.distance_lab == 1.23

    def test_to_dict_contient_toutes_les_cles(self):
        """to_dict retourne un dictionnaire avec toutes les clés."""
        result = ColorResult(
            rang=2,
            nom="bleu",
            rgb=[0, 0, 255],
            hex="#0000ff",
            pixels=50,
            proportion=0.25,
            proportion_pct=25.0,
            distance_lab=0.5,
        )

        d = result.to_dict()

        assert set(d.keys()) == {
            "rang", "nom", "rgb", "hex", "pixels",
            "proportion", "proportion_pct", "distance_lab"
        }
        assert d["nom"] == "bleu"
        assert d["pixels"] == 50

    def test_to_dict_valeurs_identiques(self):
        """to_dict ne modifie pas les valeurs."""
        result = ColorResult(
            rang=1,
            nom="vert",
            rgb=[0, 128, 0],
            hex="#008000",
            pixels=10,
            proportion=0.1,
            proportion_pct=10.0,
            distance_lab=2.0,
        )

        d = result.to_dict()

        assert d == {
            "rang": 1,
            "nom": "vert",
            "rgb": [0, 128, 0],
            "hex": "#008000",
            "pixels": 10,
            "proportion": 0.1,
            "proportion_pct": 10.0,
            "distance_lab": 2.0,
        }


# ============================================================
# Tests de la classe AnalysisMetadata.
# ============================================================

class TestAnalysisMetadata:

    def test_creation_attributs(self):
        """Les attributs sont bien stockés à la création."""
        metadata = AnalysisMetadata(
            hauteur=100,
            largeur=200,
            nombre_total_pixels=20000,
            mode_clustering="Automatique",
            nombre_clusters=4,
            score_silhouette=0.75,
        )

        assert metadata.hauteur == 100
        assert metadata.largeur == 200
        assert metadata.nombre_total_pixels == 20000
        assert metadata.mode_clustering == "Automatique"
        assert metadata.nombre_clusters == 4
        assert metadata.score_silhouette == 0.75

    def test_score_silhouette_peut_etre_none(self):
        """Le score silhouette est optionnel (mode manuel)."""
        metadata = AnalysisMetadata(
            hauteur=10,
            largeur=10,
            nombre_total_pixels=100,
            mode_clustering="Manuel",
            nombre_clusters=3,
            score_silhouette=None,
        )

        assert metadata.score_silhouette is None

    def test_to_dict_contient_toutes_les_cles(self):
        """to_dict retourne un dictionnaire avec toutes les clés."""
        metadata = AnalysisMetadata(
            hauteur=50,
            largeur=40,
            nombre_total_pixels=2000,
            mode_clustering="Manuel",
            nombre_clusters=6,
            score_silhouette=None,
        )

        d = metadata.to_dict()

        assert set(d.keys()) == {
            "hauteur", "largeur", "nombre_total_pixels",
            "mode_clustering", "nombre_clusters", "score_silhouette"
        }
        assert d["nombre_clusters"] == 6
        assert d["score_silhouette"] is None
