# ============================================================
# Couleurs de référence utilisées pour nommer les couleurs
# dominantes extraites par clustering.
# ============================================================

REFERENCE_COLORS = {
    # Tons neutres
    "noir": (0, 0, 0),
    "blanc": (255, 255, 255),
    "gris": (128, 128, 128),
    "gris clair": (211, 211, 211),
    "gris foncé": (64, 64, 64),
    "argent": (192, 192, 192),
    "beige": (245, 245, 220),
    "ivoire": (255, 255, 240),
    "crème": (253, 245, 230),
    "taupe": (72, 60, 50),
    "chocolat": (210, 105, 30),
    # Rouges / roses
    "rouge": (255, 0, 0),
    "rouge foncé": (139, 0, 0),
    "bordeaux": (128, 0, 32),
    "carmin": (150, 0, 24),
    "corail": (255, 127, 80),
    "saumon": (250, 128, 114),
    "rose": (255, 192, 203),
    "rose vif": (255, 20, 147),
    "magenta": (255, 0, 255),
    "framboise": (227, 11, 93),
    # Oranges / jaunes
    "orange": (255, 165, 0),
    "orange foncé": (255, 140, 0),
    "ambre": (255, 191, 0),
    "abricot": (251, 206, 177),
    "jaune": (255, 255, 0),
    "jaune clair": (255, 255, 224),
    "jaune doré": (218, 165, 32),
    "moutarde": (255, 219, 88),
    "or": (255, 215, 0),
    # Verts
    "vert": (0, 128, 0),
    "vert clair": (144, 238, 144),
    "vert foncé": (0, 100, 0),
    "vert lime": (50, 205, 50),
    "vert olive": (128, 128, 0),
    "vert forêt": (34, 139, 34),
    "vert menthe": (152, 255, 152),
    "vert émeraude": (80, 200, 120),
    "olive": (107, 142, 35),
    # Bleus / violets
    "bleu": (0, 0, 255),
    "bleu clair": (173, 216, 230),
    "bleu foncé": (0, 0, 139),
    "bleu marine": (25, 25, 112),
    "bleu acier": (70, 130, 180),
    "bleu ciel": (135, 206, 235),
    "bleu azur": (0, 127, 255),
    "indigo": (75, 0, 130),
    "violet": (128, 0, 128),
    "violet clair": (221, 160, 221),
    "lavande": (230, 230, 250),
    "pourpre": (128, 0, 32),
    "prune": (221, 160, 221),
    # Cyaans / turquoises
    "cyan": (0, 255, 255),
    "cyan foncé": (0, 139, 139),
    "turquoise": (64, 224, 208),
    "turquoise clair": (175, 238, 238),
    "aigue-marine": (127, 255, 212),
    "teal": (0, 128, 128),
    "menthe océan": (0, 255, 255),
    # Bruns
    "marron": (139, 69, 19),
    "marron clair": (205, 133, 63),
    "marron foncé": (101, 67, 33),
    "brun": (165, 42, 42),
    "cuivre": (184, 115, 51),
    "bronze": (205, 127, 50),
    "sépia": (112, 66, 20),
    "kaki": (189, 183, 107),
}

# ============================================================
# Formats d'image acceptés par l'application Streamlit.
# ============================================================

ALLOWED_IMAGE_FORMATS = ["jpg", "jpeg", "png", "webp"]

# ============================================================
# Couleurs de teinte disponibles pour la retouche.
# "Aucune" signifie qu'aucune teinte n'est appliquée.
# ============================================================

TINT_COLORS = {
    "Aucune": None,
    "Rouge": (255, 0, 0),
    "Orange": (255, 140, 0),
    "Jaune": (255, 215, 0),
    "Vert": (0, 180, 0),
    "Cyan": (0, 200, 200),
    "Bleu": (0, 0, 255),
    "Violet": (138, 43, 226),
    "Magenta": (255, 0, 255),
    "Rose": (255, 105, 180),
    "Blanc": (255, 255, 255),
}

# ============================================================
# Filtres artistiques disponibles pour la retouche.
# Ces noms sont aussi utilisés par ImageEditor.
# ============================================================

ARTISTIC_FILTERS = [
    "Aucun",
    "Contour",
    "Relief",
    "Détection de contours",
    "Lissage",
    "Détail",
    "Renforcement des contours",
    "Flou artistique",
]

# ============================================================
# Paramètres liés à la taille de l'image.
# ============================================================

DEFAULT_MAX_SIZE = 600
MIN_IMAGE_SIZE = 300
MAX_IMAGE_SIZE = 1000

# ============================================================
# Paramètres liés à l'échantillonnage des pixels.
# On n'utilise pas toujours tous les pixels pour accélérer
# le clustering.
# ============================================================

MAX_SAMPLES = 30000

# ============================================================
# Paramètres liés au nombre de clusters K.
# ============================================================

K_MIN = 2
K_MAX = 8

K_MANUAL_MIN = 2
K_MANUAL_MAX = 12

# ============================================================
# Graine aléatoire pour assurer la reproductibilité.
# ============================================================

RANDOM_STATE = 42