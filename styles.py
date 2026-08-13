# styles.py
#
# CSS global de l'application Streamlit.
# Centralisé dans ce module pour un style cohérent
# et facile à maintenir.

BASE_CSS = """
<style>

/* ============================================================
   Typographie et couleurs de base
   ============================================================ */

html, body, [class*="css"] {
    font-family: "Inter", "Segoe UI", system-ui, -apple-system, sans-serif;
}

.stApp {
    background: linear-gradient(180deg, #FFFFFF 0%, #F8FAFC 100%);
}

/* ============================================================
   Bandeau d'en-tête (hero)
   ============================================================ */

.hero {
    background: linear-gradient(135deg, #4F46E5 0%, #7C3AED 55%, #0EA5E9 100%);
    border-radius: 18px;
    padding: 2.2rem 2.4rem;
    color: #FFFFFF;
    margin-bottom: 1.6rem;
    box-shadow: 0 12px 30px rgba(79, 70, 229, 0.30);
    position: relative;
    overflow: hidden;
}

.hero::after {
    content: "";
    position: absolute;
    top: -60%;
    right: -10%;
    width: 340px;
    height: 340px;
    background: rgba(255, 255, 255, 0.08);
    border-radius: 50%;
}

.hero-title {
    font-size: 1.9rem;
    font-weight: 800;
    letter-spacing: -0.02em;
    margin: 0 0 0.4rem 0;
    line-height: 1.2;
}

.hero-subtitle {
    font-size: 1.02rem;
    opacity: 0.92;
    margin: 0;
    max-width: 720px;
    line-height: 1.55;
}

.hero-badges {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin-top: 1.1rem;
}

.hero-badge {
    background: rgba(255, 255, 255, 0.16);
    border: 1px solid rgba(255, 255, 255, 0.30);
    border-radius: 999px;
    padding: 4px 12px;
    font-size: 0.78rem;
    font-weight: 600;
    letter-spacing: 0.02em;
}

/* ============================================================
   Barre latérale
   ============================================================ */

[data-testid="stSidebar"] {
    background: #FFFFFF;
    border-right: 1px solid #E2E8F0;
}

[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 {
    font-size: 0.95rem;
    font-weight: 700;
    color: #1E293B;
}

[data-testid="stSidebar"] [data-testid="stExpander"] {
    border: 1px solid #E2E8F0;
    border-radius: 10px;
    background: #F8FAFC;
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
    background: linear-gradient(135deg, #4F46E5, #7C3AED);
    border: none;
    box-shadow: 0 6px 16px rgba(79, 70, 229, 0.35);
}

.stButton > button[kind="primary"]:hover {
    transform: translateY(-1px);
    box-shadow: 0 10px 22px rgba(79, 70, 229, 0.45);
}

.stButton > button:not([kind="primary"]):hover,
.stDownloadButton > button:hover {
    border-color: #4F46E5;
    color: #4F46E5;
}

/* ============================================================
   Onglets
   ============================================================ */

.stTabs [data-baseweb="tab-list"] {
    gap: 6px;
    background: #F1F5F9;
    padding: 6px;
    border-radius: 12px;
}

.stTabs [data-baseweb="tab"] {
    border-radius: 8px;
    padding: 8px 20px;
    font-weight: 600;
    color: #475569;
}

.stTabs [aria-selected="true"] {
    background: #FFFFFF;
    color: #4F46E5;
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.08);
}

/* ============================================================
   Uploader
   ============================================================ */

[data-testid="stFileUploader"] {
    background: #F8FAFC;
    border: 2px dashed #CBD5E1;
    border-radius: 14px;
    padding: 8px;
}

[data-testid="stFileUploader"]:hover {
    border-color: #4F46E5;
    background: #EEF2FF;
}

/* ============================================================
   Cartes de métriques
   ============================================================ */

[data-testid="stMetric"] {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 14px;
    padding: 18px 20px;
    box-shadow: 0 4px 14px rgba(15, 23, 42, 0.06);
}

[data-testid="stMetricLabel"] {
    font-weight: 600;
    color: #64748B;
}

[data-testid="stMetricValue"] {
    font-weight: 800;
    color: #1E293B;
}

/* ============================================================
   Tableau
   ============================================================ */

[data-testid="stDataFrame"] {
    border-radius: 12px;
    overflow: hidden;
    border: 1px solid #E2E8F0;
}

/* ============================================================
   Cadres d'image
   ============================================================ */

.img-card {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 14px;
    padding: 12px;
    box-shadow: 0 6px 18px rgba(15, 23, 42, 0.07);
    text-align: center;
    flex: 1 1 300px;
    min-width: 280px;
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
    color: #1E293B;
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
    border: 1px solid #E2E8F0;
    border-radius: 14px;
    padding: 10px;
    background: #FFFFFF;
    text-align: center;
    transition: transform 0.15s ease, box-shadow 0.15s ease;
}

.palette-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 12px 24px rgba(15, 23, 42, 0.14);
}

.palette-swatch {
    height: 56px;
    border-radius: 8px;
    border: 1px solid #E2E8F0;
}

.palette-rank {
    position: absolute;
    top: 16px;
    left: 16px;
    width: 22px;
    height: 22px;
    border-radius: 50%;
    background: rgba(15, 23, 42, 0.72);
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
    color: #1E293B;
}

.palette-meta {
    font-size: 0.75rem;
    color: #64748B;
}

.palette-hex {
    font-size: 0.72rem;
    color: #4F46E5;
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
    box-shadow: 0 2px 6px rgba(15, 23, 42, 0.15);
    transition: opacity 0.15s ease;
}

.palette-card:hover .palette-copy {
    opacity: 1;
}

.palette-copy:hover {
    background: #EEF2FF;
}

.palette-action button {
    margin-top: 14px;
    padding: 8px 18px;
    border: 1px solid #CBD5E1;
    border-radius: 10px;
    background: #F8FAFC;
    font-weight: 600;
    font-size: 0.85rem;
    color: #334155;
    cursor: pointer;
    transition: all 0.15s ease;
}

.palette-action button:hover {
    border-color: #4F46E5;
    background: #EEF2FF;
    color: #4F46E5;
}

.palette-message {
    margin-top: 10px;
    font-weight: 600;
    min-height: 18px;
    font-size: 0.85rem;
    color: #4F46E5;
}

/* ============================================================
   Sections (titres)
   ============================================================ */

.section-title {
    font-size: 1.15rem;
    font-weight: 800;
    color: #1E293B;
    margin: 0.2rem 0 0.9rem 0;
    padding-bottom: 0.4rem;
    border-bottom: 2px solid #EEF2FF;
    letter-spacing: -0.01em;
}

/* ============================================================
   Pied de page
   ============================================================ */

.footer {
    margin-top: 3rem;
    padding-top: 1.2rem;
    border-top: 1px solid #E2E8F0;
    text-align: center;
    color: #94A3B8;
    font-size: 0.8rem;
}

/* ============================================================
   Divers
   ============================================================ */

.stMarkdown hr {
    border-color: #E2E8F0;
}

[data-testid="stAlert"] {
    border-radius: 12px;
}

.stSpinner > div {
    border-top-color: #4F46E5 !important;
}

div.stBlockquote {
    border-left: 4px solid #4F46E5;
}

</style>
"""


def inject_global_css() -> None:
    """
    Injecte le CSS global dans l'application Streamlit.
    À appeler une seule fois, en début de script.
    """
    import streamlit as st

    st.markdown(BASE_CSS, unsafe_allow_html=True)
