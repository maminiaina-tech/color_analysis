# tests/test_constants.py

import pytest

from constants import (
    REFERENCE_COLORS,
    ALLOWED_IMAGE_FORMATS,
    TINT_COLORS,
    ARTISTIC_FILTERS,
    K_MIN,
    K_MAX,
    K_MANUAL_MIN,
    K_MANUAL_MAX,
)


# ============================================================
# Tests de cohérence des constantes du projet.
# ============================================================

class TestReferenceColors:

    def test_dictionnaire_non_vide(self):
        assert len(REFERENCE_COLORS) > 0

    def test_toutes_les_couleurs_sont_des_triplets_rgb(self):
        """Chaque valeur est un triplet d'entiers 0-255."""
        for nom, rgb in REFERENCE_COLORS.items():
            assert len(rgb) == 3, f"{nom} : triplet attendu"
            for canal in rgb:
                assert isinstance(canal, int)
                assert 0 <= canal <= 255, f"{nom} : canal hors limites"

    def test_noms_uniques_et_non_vides(self):
        for nom in REFERENCE_COLORS:
            assert isinstance(nom, str)
            assert nom.strip() != ""


class TestParametresClustering:

    def test_bornes_k_croisssantes(self):
        assert K_MIN < K_MAX
        assert K_MANUAL_MIN < K_MANUAL_MAX

    def test_k_manuel_plus_large_que_automatique(self):
        """Le mode manuel autorise au moins l'étendue automatique."""
        assert K_MANUAL_MIN <= K_MIN
        assert K_MANUAL_MAX >= K_MAX


class TestReglagesRetouche:

    def test_tint_colors_contient_aucune(self):
        """L'option 'Aucune' correspond à None (pas de teinte)."""
        assert TINT_COLORS.get("Aucune") is None

    def test_artistic_filters_contient_aucun(self):
        assert "Aucun" in ARTISTIC_FILTERS

    def test_formats_images_acceptes(self):
        formats_minuscules = [f.lower() for f in ALLOWED_IMAGE_FORMATS]
        for attendu in ["jpg", "jpeg", "png", "webp"]:
            assert attendu in formats_minuscules
