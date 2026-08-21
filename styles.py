# styles.py
#
# CSS de l'application Streamlit, centralisé pour un style
# cohérent et facile à maintenir.
#
# Deux contextes distincts :
#   - BASE_CSS   : styles de la page principale (hero, sidebar,
#                  boutons, onglets, etc.). Injecté une seule fois
#                  via st.markdown.
#   - IFRAME_CSS : styles des composants rendus dans st.iframe
#                  (images avant/après, palette de couleurs).
#                  Le CSS de la page parente ne s'applique pas
#                  dans une iframe : ce bloc est donc embarqué
#                  directement dans chaque srcdoc.
#
# Palette océan (sarcelle / bleu-gris / ardoise) :
#   #DCE8EB  gris bleu pâle    → fond de page
#   #EFF5F6  blanc bleuté      → fond très clair / survols
#   #B8CBD0  gris bleu         → bordures
#   #709CA7  bleu-gris         → survols / accents secondaires
#   #137C8B  sarcelle          → couleur principale
#   #7A90A4  gris ardoise      → texte secondaire / atténué
#   #344D59  ardoise foncée    → texte / accents à fort contraste


# ============================================================
# Styles de la page principale.
# ============================================================

BASE_CSS = """
<style>

/* ============================================================
   Typographie et couleurs de base
   ============================================================ */

html, body, [class*="css"] {
    font-family: "Inter", "Segoe UI", system-ui, -apple-system, sans-serif;
}

.stApp {
    background: linear-gradient(180deg, #DCE8EB 0%, #EFF5F6 100%);
}

a {
    color: #137C8B;
}

/* ============================================================
   Bandeau d'en-tête (hero) — design divisé :
   panneau gauche blanc dégradé (logo sarcelle bien visible),
   séparation oblique stylée, bordure de carte en dégradé,
   + zone droite en dégradé sarcelle (titre, texte, badges).
   ============================================================ */

.hero {
    display: flex;
    align-items: stretch;
    border: 1px solid transparent;
    border-radius: 18px;
    margin-bottom: 1.6rem;
    box-shadow: 0 12px 30px rgba(19, 124, 139, 0.18);
    overflow: hidden;
    /* Bordure en dégradé : fond blanc à l'intérieur,
       dégradé sarcelle → gris bleu sur l'anneau de bordure. */
    background:
        linear-gradient(180deg, #FFFFFF 0%, #F4F8FA 100%) padding-box,
        linear-gradient(135deg, #137C8B 0%, #709CA7 45%, #DCE8EB 100%) border-box;
}

.hero-brand {
    flex: 0 0 230px;
    display: flex;
    align-items: center;
    justify-content: center;
    /* Dégradé diagonal très doux pour dynamiquer le blanc
       sans gêner la lisibilité du logo. */
    background: linear-gradient(165deg, #FFFFFF 30%, #E4EEF2 100%);
    padding: 1.8rem 1.4rem;
}

.hero-logo {
    width: 150px;
    height: 150px;
}

.hero-main {
    position: relative;
    flex: 1 1 auto;
    min-width: 0;
    background: linear-gradient(135deg, #137C8B 0%, #709CA7 100%);
    /* Bord gauche oblique : le panneau clair s'invite en biseau. */
    clip-path: polygon(56px 0, 100% 0, 100% 100%, 0 100%);
    padding: 2rem 2.4rem 2rem calc(2.4rem + 44px);
    color: #FFFFFF;
    overflow: hidden;
}

.hero-main::after {
    content: "";
    position: absolute;
    top: -60%;
    right: -10%;
    width: 340px;
    height: 340px;
    background: rgba(255, 255, 255, 0.18);
    border-radius: 50%;
}

@media (max-width: 760px) {
    .hero {
        flex-direction: column;
    }

    .hero-brand {
        flex-basis: auto;
        padding: 1.4rem;
    }

    .hero-logo {
        width: 96px;
        height: 96px;
    }

    .hero-main {
        clip-path: none;
        padding: 1.6rem 1.4rem;
    }
}

.hero-title {
    font-size: 1.9rem;
    font-weight: 800;
    letter-spacing: -0.02em;
    margin: 0 0 0.4rem 0;
    line-height: 1.2;
    color: #FFFFFF;
}

.hero-subtitle {
    font-size: 1.02rem;
    opacity: 0.95;
    margin: 0;
    max-width: 720px;
    line-height: 1.55;
    color: rgba(255, 255, 255, 0.92);
}

.hero-badges {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin-top: 1.1rem;
}

.hero-badge {
    background: rgba(255, 255, 255, 0.14);
    border: 1px solid rgba(255, 255, 255, 0.35);
    border-radius: 999px;
    padding: 4px 12px;
    font-size: 0.78rem;
    font-weight: 600;
    letter-spacing: 0.02em;
    color: #FFFFFF;
}

/* ============================================================
   Barre latérale
   ============================================================ */

[data-testid="stSidebar"] {
    background: #FFFFFF;
    border-right: 1px solid #B8CBD0;
}

[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3,
[data-testid="stSidebar"] h4 {
    font-size: 0.95rem;
    font-weight: 700;
    color: #344D59;
}

[data-testid="stSidebar"] [data-testid="stExpander"] {
    border: 1px solid #B8CBD0;
    border-radius: 10px;
    background: #E8F1F3;
}

[data-testid="stSidebar"] [data-testid="stExpander"] summary {
    color: #344D59;
    font-weight: 600;
}

/* ============================================================
   Boutons
   ============================================================ */

.stButton > button,
.stDownloadButton > button {
    border-radius: 10px;
    font-weight: 600;
    transition: transform 0.12s ease, box-shadow 0.12s ease;
}

.stButton > button[kind="primary"] {
    background: #137C8B;
    color: #FFFFFF;
    border: none;
    box-shadow: 0 6px 16px rgba(19, 124, 139, 0.45);
}

.stButton > button[kind="primary"]:hover {
    background: #709CA7;
    color: #FFFFFF;
    transform: translateY(-1px);
    box-shadow: 0 10px 22px rgba(19, 124, 139, 0.55);
}

.stButton > button:not([kind="primary"]):hover,
.stDownloadButton > button:hover {
    border-color: #137C8B;
    color: #137C8B;
}

/* ============================================================
   Onglets
   ============================================================ */

.stTabs [data-baseweb="tab-list"] {
    gap: 6px;
    background: #DCE8EB;
    padding: 6px;
    border-radius: 12px;
}

.stTabs [data-baseweb="tab"] {
    border-radius: 8px;
    padding: 8px 20px;
    font-weight: 600;
    color: #344D59;
}

.stTabs [aria-selected="true"] {
    background: #FFFFFF;
    color: #137C8B;
    box-shadow: 0 2px 6px rgba(19, 124, 139, 0.15);
}

/* ============================================================
   Uploader
   ============================================================ */

[data-testid="stFileUploader"] {
    background: #DCE8EB;
    border: 2px dashed #709CA7;
    border-radius: 14px;
    padding: 8px;
}

[data-testid="stFileUploader"]:hover {
    border-color: #137C8B;
    background: #EFF5F6;
}

/* ============================================================
   Cartes de métriques
   ============================================================ */

[data-testid="stMetric"] {
    background: #FFFFFF;
    border: 1px solid #B8CBD0;
    border-radius: 14px;
    padding: 18px 20px;
    box-shadow: 0 4px 14px rgba(19, 124, 139, 0.10);
}

[data-testid="stMetricLabel"] {
    font-weight: 600;
    color: #7A90A4;
}

[data-testid="stMetricValue"] {
    font-weight: 800;
    color: #344D59;
}

/* ============================================================
   Tableau
   ============================================================ */

[data-testid="stDataFrame"] {
    border-radius: 12px;
    overflow: hidden;
    border: 1px solid #B8CBD0;
}

/* ============================================================
   Sections (titres)
   ============================================================ */

.section-title {
    font-size: 1.15rem;
    font-weight: 800;
    color: #344D59;
    margin: 0.2rem 0 0.9rem 0;
    padding-bottom: 0.4rem;
    border-bottom: 2px solid #B8CBD0;
    letter-spacing: -0.01em;
}

/* ============================================================
   Pied de page
   ============================================================ */

.footer {
    margin-top: 3rem;
    padding-top: 1.2rem;
    border-top: 1px solid #B8CBD0;
    text-align: center;
    color: #7A90A4;
    font-size: 0.8rem;
}

/* ============================================================
   Divers
   ============================================================ */

.stMarkdown hr {
    border-color: #B8CBD0;
}

[data-testid="stAlert"] {
    border-radius: 12px;
}

.stSpinner > div {
    border-top-color: #137C8B !important;
}

div.stBlockquote {
    border-left: 4px solid #137C8B;
}

/* Icônes Streamlit (Material Symbols) à la couleur principale */
.material-symbols-outlined {
    color: #137C8B;
}

</style>
"""


# ============================================================
# Styles embarqués dans les iframes (st.iframe / srcdoc).
# ============================================================

IFRAME_CSS = """
<style>
body {
    margin: 0;
    padding: 0;
    font-family: "Inter", "Segoe UI", system-ui, sans-serif;
}

/* ============================================================
   Cadres d'image — avant / après strictement côte à côte
   ============================================================ */

.img-pair {
    display: flex;
    flex-wrap: nowrap;
    gap: 16px;
    align-items: flex-start;
}

.img-pair .img-card {
    flex: 1 1 0;
    min-width: 0;
}

.img-card {
    background: #FFFFFF;
    border: 1px solid #B8CBD0;
    border-radius: 14px;
    padding: 12px;
    box-shadow: 0 6px 18px rgba(19, 124, 139, 0.12);
    text-align: center;
    flex: 1 1 0;
    min-width: 0;
}

.img-card img {
    max-width: 100%;
    height: auto;
    border-radius: 8px;
    display: block;
    margin: 0 auto;
}

.img-card-caption {
    margin-top: 10px;
    font-weight: 700;
    font-size: 0.9rem;
    color: #344D59;
    letter-spacing: 0.01em;
}

/* ============================================================
   Palette des couleurs
   ============================================================ */

.palette-wrap {
    display: flex;
    flex-wrap: wrap;
    gap: 14px;
}

.palette-card {
    position: relative;
    width: 148px;
    border: 1px solid #B8CBD0;
    border-radius: 14px;
    padding: 10px;
    background: #FFFFFF;
    text-align: center;
    transition: transform 0.15s ease, box-shadow 0.15s ease;
}

.palette-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 12px 24px rgba(19, 124, 139, 0.20);
}

.palette-swatch {
    height: 56px;
    border-radius: 8px;
    border: 1px solid #B8CBD0;
}

.palette-rank {
    position: absolute;
    top: 16px;
    left: 16px;
    width: 22px;
    height: 22px;
    border-radius: 50%;
    background: rgba(52, 77, 89, 0.80);
    color: #FFFFFF;
    font-size: 0.72rem;
    font-weight: 700;
    display: flex;
    align-items: center;
    justify-content: center;
}

.palette-name {
    margin-top: 8px;
    font-weight: 700;
    font-size: 0.86rem;
    color: #344D59;
}

.palette-meta {
    font-size: 0.75rem;
    color: #7A90A4;
}

.palette-hex {
    font-size: 0.72rem;
    color: #137C8B;
    font-weight: 600;
    letter-spacing: 0.03em;
}

.palette-copy {
    position: absolute;
    top: 10px;
    right: 10px;
    opacity: 0;
    cursor: pointer;
    background: rgba(255, 255, 255, 0.94);
    border-radius: 6px;
    padding: 4px;
    box-shadow: 0 2px 6px rgba(52, 77, 89, 0.18);
    transition: opacity 0.15s ease;
}

.palette-card:hover .palette-copy {
    opacity: 1;
}

.palette-copy:hover {
    background: #DCE8EB;
}

.palette-action button {
    margin-top: 14px;
    padding: 8px 18px;
    border: 1px solid #B8CBD0;
    border-radius: 10px;
    background: #E8F1F3;
    font-weight: 600;
    font-size: 0.85rem;
    color: #344D59;
    cursor: pointer;
    transition: all 0.15s ease;
}

.palette-action button:hover {
    border-color: #137C8B;
    background: #DCE8EB;
    color: #137C8B;
}

.palette-message {
    margin-top: 10px;
    font-weight: 600;
    min-height: 18px;
    font-size: 0.85rem;
    color: #137C8B;
}
</style>
"""


def inject_global_css() -> None:
    """
    Injecte le CSS de la page principale dans l'application Streamlit.
    À appeler une seule fois, en début de script.
    """
    import streamlit as st

    st.markdown(BASE_CSS, unsafe_allow_html=True)
