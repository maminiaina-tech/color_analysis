# result_renderer.py

import base64
import io
import json

import altair as alt
import pandas as pd
import streamlit as st

from typing import List

from PIL import Image

from models import ColorResult, AnalysisMetadata

from constants import (
    MIN_IMAGE_SIZE,
    MAX_IMAGE_SIZE,
    DEFAULT_MAX_SIZE,
    K_MANUAL_MIN,
    K_MANUAL_MAX,
    TINT_COLORS,
    ARTISTIC_FILTERS
)


# ============================================================
# Valeurs par défaut des réglages de retouche.
# Ces valeurs sont aussi utilisées pour réinitialiser l'interface.
# ============================================================

RETOUCH_DEFAULTS = {
    "brightness": 100,
    "contrast": 100,
    "saturation": 100,
    "sharpness": 100,
    "blur": 0.0,
    "hue": 0,
    "temperature": 0,
    "exposure": 0.0,
    "gamma": 1.0,
    "vibrance": 0,
    "red": 0,
    "green": 0,
    "blue": 0,
    "grayscale": False,
    "sepia": False,
    "invert": False,
    "vignette": 0,
    "shadows": 0,
    "highlights": 0,
    "posterize": 0,
    "solarize": 0,
    "threshold": 0,
    "grain": 0,
    "pixelate": 0,
    "tint_color": "Aucune",
    "tint_intensity": 0,
    "artistic": "Aucun",
}


# ============================================================
# Classe dédiée à l'affichage des résultats dans Streamlit.
# ============================================================

class ResultRenderer:
    """
    Cette classe contient toutes les fonctions d'affichage :

    - barre latérale de retouche ;
    - barre latérale d'analyse ;
    - images ;
    - métriques ;
    - palette ;
    - tableau ;
    - graphique ;
    - téléchargement.
    """

    # ========================================================
    # Titre de section.
    # ========================================================

    @staticmethod
    def _section_title(title: str):
        """
        Affiche un titre de section stylé.
        """
        st.markdown(
            f'<div class="section-title">{title}</div>',
            unsafe_allow_html=True,
        )

    # ========================================================
    # Affichage de la barre latérale d'analyse.
    # ========================================================

    def render_sidebar(self):
        """
        Cette fonction affiche la barre latérale d'analyse.

        Elle retourne :
        - la taille maximale de l'image ;
        - le mode de clustering ;
        - le nombre manuel de couleurs ;
        - la case pour analyser l'image retouchée.
        """

        with st.sidebar:

            st.markdown("#### 🔍 Paramètres d'analyse")

            # Étape 1 : sélection de la taille maximale.
            max_size = st.slider(
                "Taille maximale de l'image",
                min_value=MIN_IMAGE_SIZE,
                max_value=MAX_IMAGE_SIZE,
                value=DEFAULT_MAX_SIZE,
                step=50,
                help="L'image est redimensionnée pour accélérer le calcul."
            )

            # Étape 2 : sélection du mode de clustering.
            mode = st.radio(
                "Choix du nombre de couleurs",
                options=["Automatique", "Manuel"],
                horizontal=True,
                help="Le mode automatique utilise le score de silhouette."
            )

            # Étape 3 : sélection manuelle du nombre de couleurs.
            fixed_k = st.slider(
                "Nombre de couleurs",
                min_value=K_MANUAL_MIN,
                max_value=K_MANUAL_MAX,
                value=6,
                disabled=(mode == "Automatique")
            )

            # Étape 4 : choix de l'image à analyser.
            analyser_retouchee = st.checkbox(
                "Analyser l'image retouchée",
                value=False,
                help="Si coché, l'analyse se fait sur l'image modifiée."
            )

        return max_size, mode, fixed_k, analyser_retouchee

    # ========================================================
    # Bouton de lancement de l'analyse dans l'onglet.
    # ========================================================

    def render_analyze_button(self):
        """
        Cette fonction affiche le bouton de lancement de l'analyse
        dans l'onglet "Analyse des couleurs".

        Une fois l'analyse effectuée, le bouton est remplacé
        par un bouton "Réinitialiser l'analyse" qui efface
        les résultats affichés.
        """

        # Vérifie si des résultats d'analyse existent déjà.
        a_resultats = all(
            key in st.session_state
            for key in ["image_rgb", "segmented_rgb", "couleurs", "metadata"]
        )

        # Cas 1 : des résultats existent, on propose de réinitialiser.
        if a_resultats:
            if st.button(
                "↻ Réinitialiser l'analyse",
                key="reset_analysis",
                width="stretch",
            ):
                for key in [
                    "image_rgb",
                    "segmented_rgb",
                    "couleurs",
                    "metadata"
                ]:
                    st.session_state.pop(key, None)

            # On n'analyse pas à nouveau.
            return False

        # Cas 2 : aucun résultat, on propose de lancer l'analyse.
        st.markdown(
            """
            <div style="background:#EEF2FF; border:1px solid #C7D2FE;
                        border-radius:12px; padding:14px 18px; margin-bottom:12px;">
                <div style="font-weight:700; color:#312E81; font-size:0.95rem;">
                    ⚡ Prêt à analyser
                </div>
                <div style="color:#4338CA; font-size:0.85rem; margin-top:2px;">
                    Cliquez sur le bouton ci-dessous pour extraire les couleurs
                    dominantes de l'image par clustering KMeans.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        return st.button(
            "🎨 Analyser l'image",
            type="primary",
            key="analyze_button_main",
            help="Lance l'analyse des couleurs dominantes.",
            width="stretch",
        )

    # ========================================================
    # Affichage de la barre latérale de retouche.
    # ========================================================

    def render_retouch_sidebar(self) -> dict:
        """
        Cette fonction affiche les réglages de retouche
        dans la barre latérale.

        Elle retourne un dictionnaire contenant tous les réglages
        à appliquer à l'image via ImageEditor.apply().
        """

        with st.sidebar:

            st.markdown("#### 🛠️ Paramètres de retouche")

            # Bouton de réinitialisation.
            # Placé avant les widgets pour que les valeurs par défaut
            # soient bien réinjectées dans l'interface.
            if st.button(
                "↻ Réinitialiser les réglages",
                width="stretch",
            ):
                for key, value in RETOUCH_DEFAULTS.items():
                    st.session_state[key] = value

            # ================================================
            # Luminosité et couleur.
            # ================================================
            with st.expander("💡 Luminosité et couleur", expanded=False):
                brightness = st.slider(
                    "Luminosité", 50, 150, 100,
                    key="brightness"
                )
                contrast = st.slider(
                    "Contraste", 50, 150, 100,
                    key="contrast"
                )
                saturation = st.slider(
                    "Saturation", 0, 200, 100,
                    key="saturation"
                )
                exposure = st.slider(
                    "Exposition (EV)", -2.0, 2.0, 0.0, step=0.1,
                    key="exposure"
                )
                gamma = st.slider(
                    "Gamma", 0.3, 3.0, 1.0, step=0.1,
                    key="gamma"
                )
                temperature = st.slider(
                    "Température (chaud / froid)", -100, 100, 0,
                    key="temperature"
                )
                vibrance = st.slider(
                    "Vibrance", -100, 100, 0,
                    key="vibrance"
                )

            # ================================================
            # Tons, teinte et canaux.
            # ================================================
            with st.expander("🎨 Tons, teinte et canaux", expanded=True):
                shadows = st.slider(
                    "Ombres", -100, 100, 0,
                    key="shadows",
                    help="Éclaircit ou assombrit les zones sombres."
                )
                highlights = st.slider(
                    "Hautes lumières", -100, 100, 0,
                    key="highlights",
                    help="Éclaircit ou assombrit les zones claires."
                )
                hue = st.slider(
                    "Rotation de teinte", 0, 360, 0,
                    key="hue"
                )
                red = st.slider(
                    "Rouge (R)", -100, 100, 0,
                    key="red"
                )
                green = st.slider(
                    "Vert (G)", -100, 100, 0,
                    key="green"
                )
                blue = st.slider(
                    "Bleu (B)", -100, 100, 0,
                    key="blue"
                )

            # ================================================
            # Détail et effets.
            # ================================================
            with st.expander("✨ Détail et effets", expanded=False):
                sharpness = st.slider(
                    "Netteté", 0, 300, 100,
                    key="sharpness"
                )
                blur = st.slider(
                    "Flou gaussien", 0.0, 20.0, 0.0, step=0.5,
                    key="blur"
                )
                grayscale = st.checkbox(
                    "Noir et blanc",
                    key="grayscale"
                )
                sepia = st.checkbox(
                    "Sépia",
                    key="sepia"
                )
                invert = st.checkbox(
                    "Négatif",
                    key="invert"
                )
                vignette = st.slider(
                    "Vignettage", 0, 100, 0,
                    key="vignette"
                )

            # ================================================
            # Effets avancés (repliés par défaut).
            # ================================================
            with st.expander("🧪 Effets avancés", expanded=False):
                posterize = st.slider(
                    "Postérisation (niveaux)",
                    0, 8, 0,
                    key="posterize",
                    help="0 = désactivé. Réduit les niveaux de couleurs."
                )
                solarize = st.slider(
                    "Solarisation",
                    0, 255, 0,
                    key="solarize",
                    help="0 = désactivé. Inverse les couleurs au-delà du seuil."
                )
                threshold = st.slider(
                    "Seuil noir & blanc",
                    0, 255, 0,
                    key="threshold",
                    help="0 = désactivé. Convertit l'image en N&B."
                )
                grain = st.slider(
                    "Grain de film", 0, 100, 0,
                    key="grain"
                )
                pixelate = st.slider(
                    "Pixelisation (mosaïque)",
                    0, 40, 0,
                    key="pixelate",
                    help="0 = désactivé. Taille des blocs de la mosaïque."
                )

            # ================================================
            # Filtres artistiques et teinte colorée.
            # ================================================
            with st.expander("🎭 Filtres artistiques", expanded=False):
                artistic = st.selectbox(
                    "Style artistique",
                    options=ARTISTIC_FILTERS,
                    key="artistic"
                )
                tint_color = st.selectbox(
                    "Teinte colorée",
                    options=list(TINT_COLORS.keys()),
                    key="tint_color"
                )
                tint_intensity = st.slider(
                    "Intensité de la teinte", 0, 100, 0,
                    disabled=(tint_color == "Aucune"),
                    key="tint_intensity"
                )

        # Retour des réglages sous forme de dictionnaire.
        # Les clés correspondent aux paramètres de ImageEditor.apply().
        return {
            "brightness": brightness,
            "contrast": contrast,
            "saturation": saturation,
            "sharpness": sharpness,
            "blur": blur,
            "hue": hue,
            "temperature": temperature,
            "exposure": exposure,
            "gamma": gamma,
            "vibrance": vibrance,
            "red": red,
            "green": green,
            "blue": blue,
            "grayscale": grayscale,
            "sepia": sepia,
            "invert": invert,
            "vignette": vignette,
            "shadows": shadows,
            "highlights": highlights,
            "posterize": posterize,
            "solarize": solarize,
            "threshold": threshold,
            "grain": grain,
            "pixelate": pixelate,
            "tint_color": tint_color,
            "tint_intensity": tint_intensity,
            "artistic": artistic,
        }

    # ========================================================
    # Affichage de la retouche avant / après.
    # ========================================================

    def render_retouch(self, image_rgb, edited_rgb):
        """
        Cette fonction affiche l'aperçu avant / après de la retouche
        et propose le téléchargement de l'image retouchée.

        Paramètres :
        - image_rgb : image originale.
        - edited_rgb : image retouchée (déjà calculée).
        """

        st.markdown("---")
        self._section_title("Aperçu avant / après")

        # Étape 1 : affichage des deux versions côte à côte,
        # chacune dans un cadre pour bien les séparer.
        html = (
            '<div style="display:flex; flex-wrap:wrap; gap:16px; '
            'align-items:flex-start;">'
            + self._frame_html(image_rgb, "Image originale")
            + self._frame_html(edited_rgb, "Image retouchée")
            + '</div>'
        )
        st.iframe(html, height="content")

        # Étape 2 : encodage de l'image retouchée en PNG.
        buffer = io.BytesIO()
        Image.fromarray(edited_rgb.astype("uint8")).save(
            buffer,
            format="PNG"
        )

        # Étape 3 : bouton de téléchargement.
        col_dl, col_tip = st.columns([1, 2])
        with col_dl:
            st.download_button(
                label="⬇️ Télécharger l'image retouchée",
                data=buffer.getvalue(),
                file_name="image_retouchee.png",
                mime="image/png",
                key="download_retouched",
                width="stretch",
            )
        with col_tip:
            st.caption(
                "Astuce : les réglages sont appliqués en direct. "
                "Pensez à réinitialiser avant de tester un autre effet."
            )

    # ========================================================
    # Affichage complet des résultats.
    # ========================================================

    def render_results(
        self,
        image_rgb,
        segmented_rgb,
        couleurs: List[ColorResult],
        metadata: AnalysisMetadata
    ):
        """
        Cette fonction appelle toutes les fonctions d'affichage.
        """

        st.markdown("---")

        # Affichage des images.
        self._render_images(image_rgb, segmented_rgb)

        st.markdown("---")

        # Affichage des informations générales.
        self._render_metrics(metadata)

        st.markdown("---")

        # Affichage de la palette.
        self._render_palette(couleurs)

        st.markdown("---")

        # Affichage du tableau détaillé.
        self._render_table(couleurs)

        st.markdown("---")

        # Affichage du graphique.
        self._render_chart(couleurs)

        st.markdown("---")

        # Affichage des boutons de téléchargement.
        self._render_download(couleurs, metadata)

    # ========================================================
    # Affichage des images.
    # ========================================================

    def _render_images(self, image_rgb, segmented_rgb):
        """
        Affiche l'image originale et l'image segmentée.
        """

        self._section_title("Résultat visuel")

        # Affichage des deux images dans des cadres séparés.
        html = (
            '<div style="display:flex; flex-wrap:wrap; gap:16px; '
            'align-items:flex-start;">'
            + self._frame_html(image_rgb, "Image originale")
            + self._frame_html(
                segmented_rgb,
                "Image segmentée par clustering"
            )
            + '</div>'
        )
        st.iframe(html, height="content")

    # ========================================================
    # Cadre d'affichage d'une image.
    # ========================================================

    @staticmethod
    def _image_to_b64(image_rgb) -> str:
        """
        Convertit une image NumPy en URI base64 (format PNG).
        Utile pour l'afficher dans du HTML.
        """
        buffer = io.BytesIO()
        Image.fromarray(image_rgb.astype("uint8")).save(
            buffer,
            format="PNG"
        )
        data = base64.b64encode(buffer.getvalue()).decode("utf-8")
        return "data:image/png;base64," + data

    def _frame_html(self, image_rgb, caption: str) -> str:
        """
        Construit le HTML d'une image encadrée avec une légende.
        Le style est défini dans styles.py (classe .img-card).
        """
        return (
            f'<div class="img-card">'
            f'<img src="{self._image_to_b64(image_rgb)}" />'
            f'<div class="img-card-caption">{caption}</div>'
            f'</div>'
        )

    # ========================================================
    # Affichage des métriques.
    # ========================================================

    def _render_metrics(self, metadata: AnalysisMetadata):
        """
        Affiche les informations globales de l'analyse.
        """

        self._section_title("Informations générales")

        col1, col2, col3 = st.columns(3)

        # Étape 1 : nombre de couleurs détectées.
        with col1:
            st.metric(
                "Couleurs détectées",
                metadata.nombre_clusters
            )

        # Étape 2 : taille de l'image analysée.
        with col2:
            st.metric(
                "Taille analysée",
                f"{metadata.hauteur} × {metadata.largeur} px"
            )

        # Étape 3 : score silhouette.
        with col3:
            if metadata.score_silhouette is not None:
                st.metric(
                    "Score silhouette",
                    round(metadata.score_silhouette, 3)
                )
            else:
                st.metric(
                    "Score silhouette",
                    "Non calculé"
                )

        # Étape 4 : précisions complémentaires.
        col4, col5, col6 = st.columns(3)
        with col4:
            st.caption(
                f"Mode de clustering : **{metadata.mode_clustering}**"
            )
        with col5:
            st.caption(
                f"Pixels analysés : "
                f"**{metadata.nombre_total_pixels:,}**"
                .replace(",", " ")
            )

    # ========================================================
    # Affichage de la palette
    # ========================================================

    def _render_palette(self, couleurs: List[ColorResult]):
        """
        Affiche la palette des couleurs dominantes.

        Un icône de copie apparaît au passage de la souris
        sur chaque carte pour copier son code HEX.

        IMPORTANT :
        La palette est rendue dans un composant HTML qui exécute
        du JavaScript pour copier les couleurs dans le presse-papier.
        Le style est défini dans styles.py (classes .palette-*).
        """

        self._section_title("Palette des couleurs dominantes")

        # Icône SVG de copie (style "feather").
        icone_copie = (
            '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" '
            'stroke="#4F46E5" stroke-width="2" stroke-linecap="round" '
            'stroke-linejoin="round">'
            '<path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"/>'
            '<rect x="8" y="2" width="8" height="4" rx="1" ry="1"/>'
            '</svg>'
        )

        # Étape 1 : construction d'une carte par couleur.
        cartes = ""
        for rang, color in enumerate(couleurs, start=1):
            cartes += (
                # Carte de la couleur.
                f'<div class="palette-card">'
                # Rang de la couleur.
                f'<div class="palette-rank">{rang}</div>'
                # Icône de copie visible au survol.
                f'<div class="palette-copy" onclick="copier(\'{color.hex}\')" '
                f'title="Copier {color.hex}">{icone_copie}</div>'
                # Rectangle coloré.
                f'<div class="palette-swatch" '
                f'style="background-color:{color.hex};"></div>'
                # Nom de la couleur.
                f'<div class="palette-name">{color.nom}</div>'
                # Proportion et pixels.
                f'<div class="palette-meta">{color.proportion_pct} % · '
                f'{color.pixels} px</div>'
                # Code HEX.
                f'<div class="palette-hex">{color.hex}</div>'
                # Fermeture de la carte.
                f'</div>'
            )

        # Liste des codes HEX pour le bouton "Copier tout".
        hex_list = ", ".join("'" + c.hex + "'" for c in couleurs)

        # Étape 2 : assemblage du HTML + JavaScript.
        palette_html = f"""
        <div class="palette-wrap">{cartes}</div>

        <div class="palette-action">
            <button onclick="copierTout()">📋 Copier toutes les couleurs</button>
        </div>

        <div class="palette-message" id="message"></div>

        <script>
            function copier(texte) {{
                var fait = function () {{
                    document.getElementById('message').textContent =
                        'Copié : ' + texte;
                }};
                if (navigator.clipboard && window.isSecureContext) {{
                    navigator.clipboard.writeText(texte).then(fait);
                }} else {{
                    var zone = document.createElement('textarea');
                    zone.value = texte;
                    document.body.appendChild(zone);
                    zone.select();
                    document.execCommand('copy');
                    document.body.removeChild(zone);
                    fait();
                }}
            }}
            function copierTout() {{
                var liste = [{hex_list}];
                var texte = liste.join('\\n');
                var fait = function () {{
                    document.getElementById('message').textContent =
                        'Toutes les couleurs copiées !';
                }};
                if (navigator.clipboard && window.isSecureContext) {{
                    navigator.clipboard.writeText(texte).then(fait);
                }} else {{
                    var zone = document.createElement('textarea');
                    zone.value = texte;
                    document.body.appendChild(zone);
                    zone.select();
                    document.execCommand('copy');
                    document.body.removeChild(zone);
                    fait();
                }}
            }}
        </script>
        """

        # Étape 3 : affichage dans une iframe.
        # La hauteur est ajustée automatiquement au contenu.
        st.iframe(palette_html, height="content")

    # ========================================================
    # Conversion des résultats en DataFrame.
    # ========================================================

    def _to_dataframe(self, couleurs: List[ColorResult]) -> pd.DataFrame:
        """
        Convertit la liste des couleurs en tableau pandas.
        """
        return pd.DataFrame([color.to_dict() for color in couleurs])

    # ========================================================
    # Affichage du tableau détaillé.
    # ========================================================

    def _render_table(self, couleurs: List[ColorResult]):
        """
        Affiche un tableau détaillé des couleurs.
        """

        self._section_title("Tableau détaillé")

        # Étape 1 : conversion en DataFrame.
        df = self._to_dataframe(couleurs)

        # Étape 2 : renommage des colonnes en français.
        df = df[
            [
                "rang",
                "nom",
                "hex",
                "rgb",
                "pixels",
                "proportion_pct",
                "distance_lab"
            ]
        ].rename(
            columns={
                "rang": "Rang",
                "nom": "Nom",
                "hex": "Code HEX",
                "rgb": "RGB",
                "pixels": "Pixels",
                "proportion_pct": "Proportion (%)",
                "distance_lab": "Distance LAB",
            }
        )

        # Étape 3 : affichage du tableau.
        st.dataframe(
            df,
            width="stretch",
            hide_index=True,
            column_config={
                "Proportion (%)": st.column_config.NumberColumn(
                    format="%.2f"
                ),
                "Distance LAB": st.column_config.NumberColumn(
                    format="%.2f"
                ),
            },
        )

    # ========================================================
    # Affichage du graphique.
    # ========================================================

    def _render_chart(self, couleurs: List[ColorResult]):
        """
        Affiche un diagramme en barres horizontal des proportions,
        coloré avec la couleur correspondante.
        """

        self._section_title("Proportions des couleurs")

        # Étape 1 : conversion en DataFrame.
        df = self._to_dataframe(couleurs)

        # Étape 2 : ordre décroissant des proportions.
        df = df.sort_values("proportion_pct", ascending=True)

        # Étape 3 : création du graphique Altair.
        chart = (
            alt.Chart(df)
            .mark_bar(cornerRadiusEnd=6, size=26)
            .encode(
                x=alt.X(
                    "proportion_pct:Q",
                    title="Proportion (%)",
                    scale=alt.Scale(domain=[0, 100]),
                ),
                y=alt.Y(
                    "nom:N",
                    title=None,
                    sort="-x",
                ),
                color=alt.Color("hex:N", scale=None, legend=None),
                tooltip=[
                    alt.Tooltip("nom:N", title="Couleur"),
                    alt.Tooltip("hex:N", title="Code HEX"),
                    alt.Tooltip(
                        "proportion_pct:Q",
                        title="Proportion (%)",
                        format=".2f",
                    ),
                    alt.Tooltip("pixels:Q", title="Pixels", format=","),
                ],
            )
            .properties(
                height=max(300, len(couleurs) * 44),
            )
        )

        # Étape 4 : affichage du graphique.
        st.altair_chart(chart, width="stretch", theme=None)

    # ========================================================
    # Affichage des boutons de téléchargement.
    # ========================================================

    def _render_download(
        self,
        couleurs: List[ColorResult],
        metadata: AnalysisMetadata
    ):
        """
        Affiche les boutons pour télécharger JSON et CSV.
        """

        self._section_title("Téléchargement des résultats")

        # Étape 1 : création du dictionnaire JSON.
        json_data = {
            "metadata": metadata.to_dict(),
            "couleurs": [color.to_dict() for color in couleurs]
        }

        # Étape 2 : boutons de téléchargement côte à côte.
        col1, col2, col3 = st.columns(3)

        with col1:
            st.download_button(
                label="📄 Télécharger JSON",
                data=json.dumps(json_data, ensure_ascii=False, indent=2),
                file_name="analyse_couleurs.json",
                mime="application/json",
                key="download_json",
                width="stretch",
            )

        # Étape 3 : conversion en CSV.
        df = self._to_dataframe(couleurs)
        csv_data = df.to_csv(index=False).encode("utf-8")

        with col2:
            st.download_button(
                label="📊 Télécharger CSV",
                data=csv_data,
                file_name="analyse_couleurs.csv",
                mime="text/csv",
                key="download_csv",
                width="stretch",
            )
