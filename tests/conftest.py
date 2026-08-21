# tests/conftest.py

import sys
from pathlib import Path

import numpy as np
import pytest

# Permet d'importer les modules du projet (constants, models, ...)
# puisque le code source est à la racine et non dans un package.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


# ============================================================
# Fixtures d'images synthétiques pour les tests.
# ============================================================

@pytest.fixture
def image_rouge():
    """Image 4x4 entièrement rouge."""
    return np.full((4, 4, 3), (255, 0, 0), dtype=np.uint8)


@pytest.fixture
def image_bicolore():
    """
    Image 2x2 avec deux couleurs pures :
    moitié rouge, moitié bleue.
    """
    img = np.zeros((2, 2, 3), dtype=np.uint8)
    img[0, :] = (255, 0, 0)
    img[1, :] = (0, 0, 255)
    return img


@pytest.fixture
def image_degradee():
    """Petite image aléatoire reproductible (10x10)."""
    rng = np.random.default_rng(42)
    return rng.integers(0, 256, size=(10, 10, 3), dtype=np.uint8)


@pytest.fixture
def image_noire():
    """Image 4x4 entièrement noire."""
    return np.zeros((4, 4, 3), dtype=np.uint8)


@pytest.fixture
def image_blanche():
    """Image 4x4 entièrement blanche."""
    return np.full((4, 4, 3), 255, dtype=np.uint8)
