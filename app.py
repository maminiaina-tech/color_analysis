# app.py

import streamlit as st

from constants import ALLOWED_IMAGE_FORMATS

from image_processor import ImageProcessor
from color_processor import ColorProcessor
from clustering_service import ClusteringService
from color_analyzer import ColorAnalyzer
from result_renderer import ResultRenderer


# ============================================================
# Configuration générale de la page Streamlit.
# ============================================================

st.set_page_config(
    page_title="Analyse colorimétrique d'images",
    layout="wide"
)

# ============================================================
# Titre et description de l'application.
# ============================================================

st.title("Analyse colorimétrique d'images")

st.markdown(
    """
    Cette application permet d'extraire les couleurs dominantes d'une image,
    d'estimer leurs proportions et de les classer par clustering
    dans l'espace colorimétrique LAB.
    """
)

# ============================================================
# Zone d'upload de l'image.
# ============================================================

uploaded_file = st.file_uploader(
    "Téléverser une image",
    type=ALLOWED_IMAGE_FORMATS
)

# ============================================================
# Initialisation du renderer Streamlit.
# ============================================================

renderer = ResultRenderer()

# ============================================================
# Affichage de la barre latérale.
# ============================================================

max_size, mode, fixed_k, analyze_button = renderer.render_sidebar()

# ============================================================
# Logique principale.
# ============================================================

if uploaded_file is not None:

    # ========================================================
    # Étape 1 : analyse uniquement si le bouton est cliqué.
    # ========================================================
    if analyze_button:

        # Étape 2 : création des processeurs.
        image_processor = ImageProcessor(max_size=max_size)
        color_processor = ColorProcessor()
        clustering_service = ClusteringService()

        # Étape 3 : création de l'analyseur principal.
        analyzer = ColorAnalyzer(
            image_processor=image_processor,
            color_processor=color_processor,
            clustering_service=clustering_service
        )

        # Étape 4 : chargement de l'image.
        image_rgb = image_processor.load_image(uploaded_file)

        # Étape 5 : analyse de l'image.
        with st.spinner("Analyse de l'image en cours..."):
            couleurs, segmented_rgb, metadata = analyzer.analyze(
                image_rgb=image_rgb,
                mode=mode,
                fixed_k=fixed_k
            )

        # Étape 6 : sauvegarde des résultats dans session_state.
        st.session_state["image_rgb"] = image_rgb
        st.session_state["segmented_rgb"] = segmented_rgb
        st.session_state["couleurs"] = couleurs
        st.session_state["metadata"] = metadata

    # ========================================================
    # Étape 7 : affichage des résultats s'ils existent.
    # ========================================================
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

else:
    st.info("Veuillez téléverser une image pour commencer l'analyse.")