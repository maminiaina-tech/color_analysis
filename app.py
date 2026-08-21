# app.py

import base64
import io
import json
import os

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
    page_title="MamiLoko Vision",
    page_icon="logo/logo_icon.png",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# Chargement du logo (encodé en base64 pour l'intégrer au hero).
# ============================================================

def charger_logo_base64() -> str:
    """
    Retourne le logo encodé en URI base64, ou une chaîne vide
    si le fichier est introuvable.
    """
    chemin = os.path.join(os.path.dirname(__file__), "logo", "logo_hd.png")
    if not os.path.exists(chemin):
        return ""
    with open(chemin, "rb") as f:
        return "data:image/png;base64," + base64.b64encode(f.read()).decode("utf-8")


logo_uri = charger_logo_base64()

# ============================================================
# Injection du style global personnalisé.
# ============================================================

inject_global_css()


# ============================================================
# Bandeau d'en-tête (hero) avec logo.
# ============================================================

logo_html = (
    f'<img class="hero-logo" src="{logo_uri}" alt="Logo MamiLoko Vision" />'
    if logo_uri
    else ""
)

# Panneau gauche blanc réservé au logo (le logo sarcelle doit
# trancher sur un fond clair pour rester bien visible).
brand_html = f'<div class="hero-brand">{logo_html}</div>' if logo_html else ""

st.markdown(
    f"""
    <div class="hero">
        {brand_html}
        <div class="hero-main">
            <div class="hero-title">MamiLoko Vision</div>
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
    </div>
    """,
    unsafe_allow_html=True,
)

# ============================================================
# Zone d'upload de l'image.
# ============================================================

st.markdown("#### :material/cloud_upload: Téléverser une image")

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
# Helpers mis en cache (st.cache_data évite de refaire les
# calculs lourds à chaque interaction avec un widget).
# ============================================================

@st.cache_data(show_spinner=False)
def charger_image(bytes_data: bytes, max_size: int):
    """
    Charge l'image depuis les octets stockés dans la session.

    Paramètres :
    - bytes_data : octets de l'image téléversée.
    - max_size : taille maximale après redimensionnement.
    """

    processor = ImageProcessor(max_size=max_size)
    return processor.load_image(io.BytesIO(bytes_data))


@st.cache_data(show_spinner=False)
def analyser_image(image_rgb, mode: str, fixed_k: int, max_size: int):
    """
    Lance l'analyse colorimétrique complète.

    Le résultat est mis en cache : relancer l'analyse avec la
    même image et les mêmes paramètres est instantané.

    Paramètres :
    - image_rgb : image à analyser.
    - mode : "Automatique" ou "Manuel".
    - fixed_k : nombre de clusters en mode manuel.
    - max_size : taille maximale de l'image (injection dépendance).
    """

    analyzer = ColorAnalyzer(
        image_processor=ImageProcessor(max_size=max_size),
        color_processor=ColorProcessor(),
        clustering_service=ClusteringService()
    )

    return analyzer.analyze(
        image_rgb=image_rgb,
        mode=mode,
        fixed_k=fixed_k
    )


# ============================================================
# Initialisation du renderer Streamlit.
# ============================================================

renderer = ResultRenderer()

# ============================================================
# Logique principale.
# ============================================================

if uploaded_file is None:

    col_centre1, col_centre2, col_centre3 = st.columns([1, 2, 1])
    with col_centre2:
        with st.container(border=True):
            st.markdown("## :material/image: Aucune image pour le moment")
            st.write(
                "Téléversez une image ci-dessus pour commencer la retouche "
                "et l'analyse des couleurs."
            )

else:

    # ========================================================
    # Étape 1 : chargement de l'image originale.
    # ========================================================
    original_rgb = charger_image(
        st.session_state["uploaded_bytes"],
        DEFAULT_MAX_SIZE
    )

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
    # Étape 5 : signature des paramètres d'analyse.
    # ========================================================
    # Permet de détecter un changement de paramètres et de
    # proposer une nouvelle analyse sans réinitialiser manuellement.
    signature = (
        max_size,
        mode,
        fixed_k,
        analyser_retouchee,
        json.dumps(adjustments, sort_keys=True) if analyser_retouchee else "",
    )

    # ========================================================
    # Étape 6 : onglets Retouche / Analyse.
    # ========================================================
    tab_retouche, tab_analyse = st.tabs(
        [":material/tune: Retouche d'image", ":material/palette: Analyse des couleurs"]
    )

    # --------------------------------------------------------
    # Onglet 1 : retouche (avant / après en temps réel).
    # --------------------------------------------------------
    with tab_retouche:
        renderer.render_retouch(original_rgb, edited_rgb)
        renderer.render_histogram(original_rgb, edited_rgb)

    # --------------------------------------------------------
    # Onglet 2 : analyse des couleurs.
    # --------------------------------------------------------
    with tab_analyse:

        # Bouton de lancement de l'analyse dans l'onglet.
        analyze_button = renderer.render_analyze_button(signature)

        # Image utilisée pour l'analyse.
        base_image = (
            edited_rgb
            if analyser_retouchee
            else charger_image(st.session_state["uploaded_bytes"], max_size)
        )

        # Analyse uniquement si le bouton est cliqué.
        if analyze_button:

            # Analyse de l'image (mise en cache).
            with st.spinner("Analyse de l'image en cours..."):
                couleurs, segmented_rgb, metadata = analyser_image(
                    image_rgb=base_image,
                    mode=mode,
                    fixed_k=fixed_k,
                    max_size=max_size
                )

            # Sauvegarde des résultats dans session_state.
            st.session_state["image_rgb"] = base_image
            st.session_state["segmented_rgb"] = segmented_rgb
            st.session_state["couleurs"] = couleurs
            st.session_state["metadata"] = metadata
            st.session_state["analysis_signature"] = signature

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
        MamiLoko Vision · Retouche &amp; analyse colorimétrique d'images
    </div>
    """,
    unsafe_allow_html=True,
)
