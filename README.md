# MamiLoko Vision

<p align="center">
  <img src="logo/logo_hd.png" alt="Logo MamiLoko Vision" width="180" />
</p>

**MamiLoko Vision : analyse colorimétrique d'images — extraction automatique des couleurs dominantes, estimation de leurs proportions et classification par clustering.**

Application web développée avec **Python** et **Streamlit**.

---

## Interface et design

L'interface a été conçue pour un rendu professionnel :

- **Thème personnalisé** défini dans `.streamlit/config.toml` (palette océan : sarcelle, bleu-gris, ardoise) ;
- **Logo dédié** (`logo/logo.png`, décliné en `logo_hd.png`, `logo.svg` et icône `logo_icon.png`) : affiché dans le bandeau d'en-tête et comme icône d'onglet ;
- **Bandeau d'en-tête** (hero) avec dégradé, logo et badges récapitulatifs des fonctionnalités ;
- **CSS global centralisé** dans `styles.py` : cartes de métriques, cadres d'images, palette de couleurs avec rang, effet de survol, copie des codes HEX ;
- **Barre latérale organisée** en sections repliables (luminosité, tons, détail, effets avancés, filtres artistiques) ;
- **Histogrammes avant / après** dans l'onglet retouche (style Photoshop / Lightroom) : luminance avec zones tonales (ombres, tons moyens, hautes lumières), canaux Rouge / Vert / Bleu superposés, et statistiques comparatives (moyenne, médiane, écart-type) — mise à jour en direct à chaque réglage ;
- **Graphique des proportions** coloré avec la couleur correspondante (Altair) ;
- **Tableau détaillé** avec colonnes renommées et formatage.

---

## Contexte

Ce projet consiste à analyser une image uploadée par l'utilisateur afin d'en extraire les couleurs dominantes, d'estimer leurs proportions et de les classifier automatiquement par clustering dans l'espace colorimétrique **LAB**, plus proche de la perception humaine que l'espace RGB.

---

## Objectifs

- Uploader une image (JPG, JPEG, PNG, WEBP) ;
- Retoucher l'image en temps réel et visualiser l'histogramme de luminance avant / après ;
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
| pytest           | Tests unitaires                         |

---

## Tests unitaires

Le projet dispose d'une suite de **94 tests unitaires** (pytest) couvrant toute la logique métier : conversions colorimétriques, clustering, pipeline d'analyse, retouche, histogrammes, modèles de données et constantes.

### Installation

```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### Exécution

```bash
# Lancer toute la suite
pytest

# Avec rapport de couverture
pytest --cov=. --cov-report=term-missing

# Lancer un seul module de tests
pytest tests/test_color_analyzer.py
```

### Organisation

| Fichier de test              | Contenu testé                                              | Nb |
|------------------------------|------------------------------------------------------------|----|
| `test_constants.py`          | Cohérence des constantes (RGB valides, bornes K)            | 8  |
| `test_models.py`             | Dataclasses `ColorResult` / `AnalysisMetadata`, `to_dict()` | 6  |
| `test_color_processor.py`    | Conversions RGB ↔ LAB ↔ HEX, nommage ΔE                     | 14 |
| `test_image_processor.py`    | Échantillonnage, reconstruction segmentée, chargement       | 10 |
| `test_clustering_service.py` | KMeans, reproductibilité, choix automatique de K            | 9  |
| `test_color_analyzer.py`     | Pipeline complet (proportions, tri, métadonnées)            | 10 |
| `test_histogram_processor.py`| Luminance, histogrammes, statistiques tonales               | 19 |
| `test_image_editor.py`       | Réglages de retouche (négatif, seuil, teinte, vignette…)    | 18 |

Les modules d'interface (`app.py`, `result_renderer.py`, `styles.py`) ne sont pas couverts par les tests unitaires : ils dépendent du runtime Streamlit et relèvent de tests d'intégration.

Les fixtures partagées (images synthétiques rouge, bicolore, dégradée, noire, blanche) sont définies dans `tests/conftest.py`. La configuration pytest se trouve dans `pytest.ini`.

---

## Structure du projet

```text
mamiloko-vision/
│
├── app.py                  # Point d'entrée de l'application Streamlit
├── constants.py            # Constantes et paramètres du projet
├── models.py               # Classes de résultats (ColorResult, AnalysisMetadata)
├── image_processor.py      # Classe ImageProcessor
├── image_editor.py         # Classe ImageEditor (retouche façon Photoshop)
├── histogram_processor.py  # Classe HistogramProcessor (histogramme de luminance)
├── color_processor.py      # Classe ColorProcessor
├── clustering_service.py   # Classe ClusteringService
├── color_analyzer.py       # Classe ColorAnalyzer (orchestration)
├── result_renderer.py      # Classe ResultRenderer (interface Streamlit)
├── styles.py               # CSS global de l'interface
├── .streamlit/config.toml  # Thème et configuration Streamlit
├── requirements.txt        # Dépendances Python
├── requirements-dev.txt    # Dépendances de développement (pytest, pytest-cov)
├── pytest.ini              # Configuration des tests unitaires
├── tests/                  # Suite de tests unitaires (94 tests)
│   ├── conftest.py         # Fixtures partagées (images synthétiques)
│   ├── test_constants.py
│   ├── test_models.py
│   ├── test_color_processor.py
│   ├── test_image_processor.py
│   ├── test_clustering_service.py
│   ├── test_color_analyzer.py
│   ├── test_histogram_processor.py
│   └── test_image_editor.py
├── .gitignore              # Fichiers à ignorer par Git
├── logo/                   # Logo du projet (PNG, SVG, icône) et assets
├── docs/                   # Documentation (LaTeX, Markdown, PDF, compile_pdf.py)
└── README.md               # Documentation du projet
