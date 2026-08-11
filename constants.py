# ============================================================
# Couleurs de référence utilisées pour nommer les couleurs
# dominantes extraites par clustering.
# ============================================================

REFERENCE_COLORS = {
    "noir": (0, 0, 0),
    "blanc": (255, 255, 255),
    "gris": (128, 128, 128),
    "rouge": (255, 0, 0),
    "vert": (0, 128, 0),
    "bleu": (0, 0, 255),
    "jaune": (255, 255, 0),
    "orange": (255, 165, 0),
    "violet": (128, 0, 128),
    "rose": (255, 192, 203),
    "marron": (139, 69, 19),
    "cyan": (0, 255, 255),
    "beige": (245, 245, 220),
    "turquoise": (64, 224, 208),
}

# ============================================================
# Formats d'image acceptés par l'application Streamlit.
# ============================================================

ALLOWED_IMAGE_FORMATS = ["jpg", "jpeg", "png", "webp"]

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