# result_renderer.py

import json

import pandas as pd
import streamlit as st

from typing import List

from models import ColorResult, AnalysisMetadata

from constants import (
    MIN_IMAGE_SIZE,
    MAX_IMAGE_SIZE,
    DEFAULT_MAX_SIZE,
    K_MANUAL_MIN,
    K_MANUAL_MAX
)


# ============================================================
# Classe dédiée à l'affichage des résultats dans Streamlit.
# ============================================================

class ResultRenderer:
    """
    Cette classe contient toutes les fonctions d'affichage :

    - barre latérale ;
    - images ;
    - métriques ;
    - palette ;
    - tableau ;
    - graphique ;
    - téléchargement.
    """

    # ========================================================
    # Affichage de la barre latérale.
    # ========================================================

    def render_sidebar(self):
        """
        Cette fonction affiche la barre latérale.

        Elle retourne :
        - la taille maximale de l'image ;
        - le mode de clustering ;
        - le nombre manuel de couleurs ;
        - le bouton d'analyse.
        """

        with st.sidebar:

            st.header("Paramètres d'analyse")

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

            # Étape 4 : bouton de lancement de l'analyse.
            analyze_button = st.button(
                "Analyser l'image",
                type="primary"
            )

        return max_size, mode, fixed_k, analyze_button

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

        st.subheader("Résultat visuel")

        col1, col2 = st.columns(2)

        # Étape 1 : affichage de l'image originale.
        with col1:
            st.image(image_rgb, caption="Image originale")

        # Étape 2 : affichage de l'image segmentée.
        with col2:
            st.image(segmented_rgb, caption="Image segmentée par clustering")

    # ========================================================
    # Affichage des métriques.
    # ========================================================

    def _render_metrics(self, metadata: AnalysisMetadata):
        """
        Affiche les informations globales de l'analyse.
        """

        st.subheader("Informations générales")

        col1, col2, col3 = st.columns(3)

        # Étape 1 : nombre de couleurs détectées.
        with col1:
            st.metric(
                "Nombre de couleurs détectées",
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

    # ========================================================
    # Fonction utilitaire d'affichage HTML.
    # ========================================================

    @staticmethod
    def _display_html(html_content: str):
        """
        Affiche du HTML dans Streamlit.

        """

        if hasattr(st, "html"):
            st.html(html_content)
        else:
            st.markdown(html_content, unsafe_allow_html=True)

    # ========================================================
    # Affichage de la palette
    # ========================================================

    def _render_palette(self, couleurs: List[ColorResult]):
        """
        Affiche la palette des couleurs dominantes.

        IMPORTANT :
        Chaque balise HTML est écrite sur UNE SEULE LIGNE.
        Sinon, Streamlit affiche le contenu du style
        comme du texte brut.
        """

        st.subheader("Palette des couleurs dominantes")

        # Étape 1 : début du conteneur flexible.
        palette_html = '<div style="display:flex;flex-wrap:wrap;gap:12px;">'

        # Étape 2 : construction d'une carte par couleur.
        for color in couleurs:
            palette_html += (
                # Carte de la couleur (une seule ligne).
                f'<div style="width:140px;border:1px solid #ddd;border-radius:10px;padding:10px;text-align:center;font-family:Arial;">'
                # Rectangle coloré (une seule ligne).
                f'<div style="height:45px;background-color:{color.hex};border-radius:6px;border:1px solid #000;"></div>'
                # Nom de la couleur (une seule ligne).
                f'<div style="margin-top:8px;font-weight:bold;">{color.nom}</div>'
                # Proportion en pourcentage (une seule ligne).
                f'<div style="font-size:14px;">{color.proportion_pct} %</div>'
                # Nombre de pixels (une seule ligne).
                f'<div style="font-size:12px;color:#555;">{color.pixels} pixels</div>'
                # Code HEX (une seule ligne).
                f'<div style="font-size:12px;color:#555;">{color.hex}</div>'
                # Fermeture de la carte.
                f'</div>'
            )

        # Étape 3 : fermeture du conteneur.
        palette_html += '</div>'

        # Étape 4 : affichage du HTML.
        self._display_html(palette_html)

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

        st.subheader("Tableau détaillé")

        # Étape 1 : conversion en DataFrame.
        df = self._to_dataframe(couleurs)

        # Étape 2 : affichage du tableau.
        st.dataframe(
            df[
                [
                    "rang",
                    "nom",
                    "hex",
                    "rgb",
                    "pixels",
                    "proportion_pct",
                    "distance_lab"
                ]
            ],
            width="stretch"
        )

    # ========================================================
    # Affichage du graphique.
    # ========================================================

    def _render_chart(self, couleurs: List[ColorResult]):
        """
        Affiche un diagramme en barres des proportions.
        """

        st.subheader("Proportions des couleurs")

        # Étape 1 : conversion en DataFrame.
        df = self._to_dataframe(couleurs)

        # Étape 2 : création d'un label plus lisible.
        df["label"] = df["nom"] + " (" + df["hex"] + ")"

        # Étape 3 : affichage du graphique.
        chart_data = df.set_index("label")["proportion_pct"]
        st.bar_chart(chart_data)

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

        st.subheader("Téléchargement des résultats")

        # Étape 1 : création du dictionnaire JSON.
        json_data = {
            "metadata": metadata.to_dict(),
            "couleurs": [color.to_dict() for color in couleurs]
        }

        # Étape 2 : bouton de téléchargement JSON.
        st.download_button(
            label="Télécharger JSON",
            data=json.dumps(json_data, ensure_ascii=False, indent=2),
            file_name="analyse_couleurs.json",
            mime="application/json",
            key="download_json"
        )

        # Étape 3 : conversion en CSV.
        df = self._to_dataframe(couleurs)
        csv_data = df.to_csv(index=False).encode("utf-8")

        # Étape 4 : bouton de téléchargement CSV.
        st.download_button(
            label="Télécharger CSV",
            data=csv_data,
            file_name="analyse_couleurs.csv",
            mime="text/csv",
            key="download_csv"
        )