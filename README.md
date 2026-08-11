# Analyse colorimétrique d'images

**Analyse colorimétrique d'images : extraction automatique des couleurs dominantes, estimation de leurs proportions et classification par clustering.**

Application web développée avec **Python** et **Streamlit**, dans le cadre du cours d'**analyse d'images / vision par ordinateur** (Master 2).

---

## Contexte

Ce projet consiste à analyser une image uploadée par l'utilisateur afin d'en extraire les couleurs dominantes, d'estimer leurs proportions et de les classifier automatiquement par clustering dans l'espace colorimétrique **LAB**, plus proche de la perception humaine que l'espace RGB.

---

## Objectifs

- Uploader une image (JPG, JPEG, PNG, WEBP) ;
- Extraire automatiquement les couleurs dominantes ;
- Estimer la proportion de chaque couleur (pixels et pourcentage) ;
- Classifier les couleurs par clustering (KMeans) ;
- Nommer approximativement chaque couleur (rouge, bleu, gris, etc.) ;
- Générer une image segmentée par clusters ;
- Exporter les résultats en JSON et CSV.

---

## Méthodologie

Le pipeline d'analyse suit les étapes suivantes :

1. **Upload** de l'image ;
2. **Redimensionnement** pour accélérer les calculs ;
3. **Conversion RGB → LAB** (espace perceptuel) ;
4. **Échantillonnage** des pixels ;
5. **Choix du nombre de clusters K** (automatique par score de silhouette, ou manuel) ;
6. **Clustering KMeans** ;
7. **Calcul des proportions** de chaque cluster ;
8. **Conversion LAB → RGB** des centres de clusters ;
9. **Reconstruction de l'image segmentée** ;
10. **Nommage des couleurs** par distance LAB aux couleurs de référence ;
11. **Affichage et export** des résultats.

---

## Technologies utilisées

| Technologie      | Rôle                                    |
|------------------|-----------------------------------------|
| Python           | Langage principal                       |
| Streamlit        | Interface web                           |
| NumPy            | Manipulation des tableaux de pixels     |
| pandas           | Tableaux de résultats et export CSV     |
| scikit-learn     | Clustering KMeans et score silhouette   |
| scikit-image     | Conversions colorimétriques RGB ↔ LAB   |
| Pillow           | Lecture et redimensionnement des images |

---

## Structure du projet

```text
analyse_couleurs/
│
├── app.py                  # Point d'entrée de l'application Streamlit
├── constants.py            # Constantes et paramètres du projet
├── models.py               # Classes de résultats (ColorResult, AnalysisMetadata)
├── image_processor.py      # Classe ImageProcessor
├── color_processor.py      # Classe ColorProcessor
├── clustering_service.py   # Classe ClusteringService
├── color_analyzer.py       # Classe ColorAnalyzer (orchestration)
├── result_renderer.py      # Classe ResultRenderer (interface Streamlit)
├── requirements.txt        # Dépendances Python
├── .gitignore              # Fichiers à ignorer par Git
└── README.md               # Documentation du projet