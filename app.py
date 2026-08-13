# app.py

import io

import streamlit as st

from constants import ALLOWED_IMAGE_FORMATS, DEFAULT_MAX_SIZE

from styles import inject_global_css

from image_processor import ImageProcessor
from color_processor import ColorProcessor
from clustering_service import ClusteringService
from color_analyzer import ColorAnalyzer
from result_renderer import ResultRenderer
from image_editor import ImageEditor


# ============================================================
# Configuration générale de la page Streamlit.
# ============================================================

st.set_page_config(
    page_title="Chroma Studio — Analyse & retouche d'images",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================
# Injection du style global personnalisé.
# ============================================================

inject_global_css()


# ============================================================
# Bandeau d'en-tête (hero).
# ============================================================

st.markdown(
    """
    <div class="hero">
        <div class="hero-title">Chroma Studio</div>
        <div class="hero-subtitle">
            Analyse colorimétrique professionnelle et retouche d'image en temps réel.
            Téléversez une photo, retouchez-la, puis extrayez automatiquement
            ses couleurs dominantes grâce au clustering.
        </div>
        <div class="hero-badges">
            <span class="hero-badge">Retouche en direct</span>
            <span class="hero-badge">Clustering KMeans</span>
            <span class="hero-badge">Espace colorimétrique LAB</span>
            <span class="hero-badge">Export JSON &amp; CSV</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ============================================================
# Zone d'upload de l'image.
# ============================================================

st.markdown(
    """
    <div style="display:flex; align-items:baseline; gap:10px; margin-bottom:2px;">
        <span style="font-size:1.05rem; font-weight:700; color:#1E293B;">
            📤 Téléverser une image
        </span>
    </div>
    """,
    unsafe_allow_html=True,
)

uploaded_file = st.file_uploader(
    "Choisissez une image au format JPG, PNG ou WEBP",
    type=ALLOWED_IMAGE_FORMATS,
    label_visibility="collapsed",
)

# Conservation des octets de l'image pour pouvoir la réutiliser
# sans avoir à la téléverser à nouveau.
if uploaded_file is not None:
    st.session_state["uploaded_bytes"] = uploaded_file.getvalue()


# ============================================================
# Helper de chargement de l'image depuis la session.
# ============================================================

def charger_image(max_size: int):
    """
    Charge l'image depuis les octets stockés dans la session.

    Paramètre :
    - max_size : taille maximale après redimensionnement.
    """

    bytes_data = st.session_state.get("uploaded_bytes")
    if bytes_data is None:
        return None

    processor = ImageProcessor(max_size=max_size)
    return processor.load_image(io.BytesIO(bytes_data))


# ============================================================
# Initialisation du renderer Streamlit.
# ============================================================

renderer = ResultRenderer()

# ============================================================
# Logique principale.
# ============================================================

if uploaded_file is None:

    st.markdown(
        """
        <div style="background:#EEF2FF; border:1px solid #C7D2FE; border-radius:14px;
                    padding:22px 24px; margin-top:10px; text-align:center;">
            <div style="font-size:2rem;">🖼️</div>
            <div style="font-size:1.05rem; font-weight:700; color:#312E81; margin-top:6px;">
                Aucune image pour le moment
            </div>
            <div style="color:#4338CA; font-size:0.9rem; margin-top:4px;">
                Téléversez une image ci-dessus pour commencer la retouche
                et l'analyse des couleurs.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

else:

    # ========================================================
    # Étape 1 : chargement de l'image originale.
    # ========================================================
    original_rgb = charger_image(DEFAULT_MAX_SIZE)

    # ========================================================
    # Étape 2 : réglages de retouche dans la barre latérale.
    # ========================================================
    adjustments = renderer.render_retouch_sidebar()

    # ========================================================
    # Étape 3 : paramètres d'analyse dans la barre latérale.
    # ========================================================
    max_size, mode, fixed_k, analyser_retouchee = (
        renderer.render_sidebar()
    )

    # ========================================================
    # Étape 4 : application des réglages en temps réel.
    # ========================================================
    editor = ImageEditor()
    edited_rgb = editor.apply(original_rgb, **adjustments)

    # ========================================================
    # Étape 5 : onglets Retouche / Analyse.
    # ========================================================
    tab_retouche, tab_analyse = st.tabs(
        ["🛠️ Retouche d'image", "🎨 Analyse des couleurs"]
    )

    # --------------------------------------------------------
    # Onglet 1 : retouche (avant / après en temps réel).
    # --------------------------------------------------------
    with tab_retouche:
        renderer.render_retouch(original_rgb, edited_rgb)

    # --------------------------------------------------------
    # Onglet 2 : analyse des couleurs.
    # --------------------------------------------------------
    with tab_analyse:

        # Bouton de lancement de l'analyse dans l'onglet.
        analyze_button = renderer.render_analyze_button()

        # Image utilisée pour l'analyse.
        base_image = (
            edited_rgb
            if analyser_retouchee
            else charger_image(max_size)
        )

        # Analyse uniquement si le bouton est cliqué.
        if analyze_button:

            # Création des processeurs.
            color_processor = ColorProcessor()
            clustering_service = ClusteringService()

            # Création de l'analyseur principal.
            analyzer = ColorAnalyzer(
                image_processor=ImageProcessor(max_size=max_size),
                color_processor=color_processor,
                clustering_service=clustering_service
            )

            # Analyse de l'image.
            with st.spinner("Analyse de l'image en cours..."):
                couleurs, segmented_rgb, metadata = analyzer.analyze(
                    image_rgb=base_image,
                    mode=mode,
                    fixed_k=fixed_k
                )

            # Sauvegarde des résultats dans session_state.
            st.session_state["image_rgb"] = base_image
            st.session_state["segmented_rgb"] = segmented_rgb
            st.session_state["couleurs"] = couleurs
            st.session_state["metadata"] = metadata

        # Affichage des résultats s'ils existent.
        if all(
            key in st.session_state
            for key in ["image_rgb", "segmented_rgb", "couleurs", "metadata"]
        ):
            renderer.render_results(
                image_rgb=st.session_state["image_rgb"],
                segmented_rgb=st.session_state["segmented_rgb"],
                couleurs=st.session_state["couleurs"],
                metadata=st.session_state["metadata"]
            )

# ============================================================
# Pied de page.
# ============================================================

st.markdown(
    """
    <div class="footer">
        Chroma Studio · Projet de vision par ordinateur (Master 2) ·
        Retouche &amp; analyse colorimétrique d'images
    </div>
    """,
    unsafe_allow_html=True,
)
