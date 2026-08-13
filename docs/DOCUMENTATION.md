# ImageSense — Documentation technique

**ImageSense : analyse colorimétrique d'images — extraction automatique des couleurs dominantes, estimation des proportions et classification par clustering, avec retouche d'image en temps réel.**

Application web **Python + Streamlit** · Espace colorimétrique **LAB** · Clustering **KMeans** · Score de **silhouette**.

---

## Table des matières

1. [Résumé](#1-résumé)
2. [Abstract](#2-abstract)
3. [Introduction](#3-introduction)
4. [Contexte et objectifs](#4-contexte-et-objectifs)
5. [Architecture logicielle](#5-architecture-logicielle)
   - 5.1 Vue d'ensemble
   - 5.2 Description des modules
   - 5.3 Cycle de vie de l'application
6. [Modèles mathématiques](#6-modèles-mathématiques)
   - 6.1 Espace colorimétrique CIELAB
   - 6.2 Conversion RGB → LAB
   - 6.3 Luminance perceptuelle (Rec. 601)
   - 6.4 Échantillonnage aléatoire des pixels
   - 6.5 Clustering KMeans
   - 6.6 Choix automatique de K — score de silhouette
   - 6.7 Calcul des proportions
   - 6.8 Nommage des couleurs — distance ΔE
   - 6.9 Histogramme de luminance et statistiques tonales
   - 6.10 Modèles de retouche d'image
7. [Pipeline d'analyse](#7-pipeline-danalyse)
8. [Interface utilisateur](#8-interface-utilisateur)
9. [Exports de données](#9-exports-de-données)
10. [Complexité et performances](#10-complexité-et-performances)
11. [Limites connues](#11-limites-connues)
12. [Conclusion](#12-conclusion)

---

## 1. Résumé

ImageSense est une application web d'analyse colorimétrique et de retouche d'image en temps réel. L'utilisateur téléverse une image (JPG, PNG, WEBP), la retouche via une barre latérale inspirée de Photoshop (luminosité, contraste, saturation, gamma, exposition, température, vibrance, vignettage, filtres artistiques…), puis lance une analyse qui extrait automatiquement les **couleurs dominantes**, estime leurs **proportions** et les classe par **clustering KMeans** dans l'espace perceptuel **CIELAB**.

Le nombre de couleurs est soit choisi manuellement, soit déterminé automatiquement par optimisation du **score de silhouette** sur un intervalle K ∈ [2, 8]. Chaque couleur extraite est nommée approximativement (bleu, vert, gris…) par recherche du plus proche voisin dans un dictionnaire de 67 couleurs de référence, mesuré par **distance euclidienne dans LAB (ΔE)**.

Le pipeline repose sur : conversion **RGB → LAB**, échantillonnage aléatoire (≤ 30 000 pixels), entraînement **KMeans** (10 initialisations), calcul des proportions par comptage de clusters, reconstruction d'une **image segmentée**, puis rendu interactif (palette, graphique de proportions Altair, tableau détaillé) et **export JSON / CSV**. Une fonctionnalité de retouche intégrée affiche les **histogrammes de luminance avant/après** (ombres, tons moyens, hautes lumières) avec statistiques comparatives, le tout mis à jour en direct.

**Mots-clés :** vision par ordinateur, couleurs dominantes, CIELAB, KMeans, score de silhouette, histogramme, retouche d'image, Streamlit.

---

## 2. Abstract

ImageSense is a web application for colorimetric image analysis and real-time photo editing. The user uploads an image (JPG, PNG, WEBP), edits it through a Photoshop-inspired sidebar (brightness, contrast, saturation, gamma, exposure, temperature, vibrance, vignetting, artistic filters…), then triggers an analysis that automatically extracts **dominant colors**, estimates their **proportions**, and classifies them via **KMeans clustering** in the perceptually-uniform **CIELAB** color space.

The number of colors is either set manually or selected automatically by maximizing the **silhouette score** over K ∈ [2, 8]. Each extracted color is roughly named (blue, green, gray…) by nearest-neighbor search against a dictionary of 67 reference colors, using **Euclidean distance in LAB space (ΔE)**.

The pipeline relies on: **RGB → LAB** conversion, random pixel sampling (≤ 30,000 pixels), **KMeans** training (10 initializations), proportion computation by cluster counting, reconstruction of a **segmented image**, then interactive rendering (palette, Altair proportion chart, detailed table) and **JSON / CSV export**. An integrated editing module displays **before/after luminance histograms** (shadows, midtones, highlights) with comparative statistics, updated live.

**Keywords:** computer vision, dominant colors, CIELAB, KMeans, silhouette score, histogram, image editing, Streamlit.

---

## 3. Introduction

L'analyse des couleurs d'une image est un problème classique de vision par ordinateur, utilisé dans les domaines du design, du marketing, de la photographie et du e-commerce. L'objectif est de réduire une image (des centaines de milliers de pixels) à un petit ensemble de couleurs représentatives accompagnées de leurs proportions.

La difficulté principale est que l'espace **RGB** n'est pas **perceptuellement uniforme** : une distance euclidienne dans RGB ne reflète pas la distance perçue par l'œil humain. ImageSense répond à ce problème en travaillant dans l'espace **CIELAB**, conçu pour que la distance euclidienne y approxime la différence perceptuelle, et en utilisant **KMeans** pour regrouper les pixels en clusters de couleurs dominantes.

Ce document présente l'architecture du projet, puis détaille les modèles mathématiques sous-jacents (conversions colorimétriques, clustering, métriques de qualité, modèles de retouche).

---

## 4. Contexte et objectifs

Le projet part d'un constat : extraire les couleurs dominantes d'une image de façon fiable nécessite un espace colorimétrique perceptuel et une méthode de clustering robuste. Le score de silhouette permet en outre d'automatiser le choix du nombre de couleurs.

**Objectifs fonctionnels :**

- Téléverser une image (JPG, JPEG, PNG, WEBP) ;
- Retoucher l'image en temps réel et visualiser l'histogramme de luminance avant / après ;
- Extraire automatiquement les couleurs dominantes ;
- Estimer la proportion de chaque couleur (pixels et pourcentage) ;
- Classifier les couleurs par clustering (KMeans) ;
- Choisir le nombre de couleurs automatiquement (silhouette) ou manuellement ;
- Nommer approximativement chaque couleur (rouge, bleu, gris, etc.) ;
- Générer une image segmentée par clusters ;
- Exporter les résultats en JSON et CSV.

**Contraintes techniques :**

- Limiter le temps de calcul par redimensionnement (taille max 1000 px) et échantillonnage (≤ 30 000 pixels) ;
- Assurer la reproductibilité via une graine aléatoire fixe (`RANDOM_STATE = 42`) ;
- Réaliser tous les traitements avec NumPy / scikit-learn / scikit-image.

---

## 5. Architecture logicielle

### 5.1 Vue d'ensemble

L'application suit une architecture modulaire à **injection de dépendances** : le module central `ColorAnalyzer` orchestre des services indépendants, ce qui facilite les tests et la maintenance.

```text
ImageSense/
│
├── app.py                  # Point d'entrée Streamlit (orchestration UI)
├── constants.py            # Constantes : couleurs de référence, bornes K, seuils
├── models.py               # Dataclasses ColorResult, AnalysisMetadata
├── image_processor.py      # Chargement, redimensionnement, échantillonnage, reconstruction
├── image_editor.py         # Retouche façon Photoshop (27 réglages)
├── histogram_processor.py  # Histogrammes luminance/canaux, statistiques tonales
├── color_processor.py      # Conversions RGB↔LAB, RGB→HEX, nommage des couleurs
├── clustering_service.py   # KMeans, choix automatique de K (silhouette)
├── color_analyzer.py       # Pipeline d'analyse complet (orchestrateur)
├── result_renderer.py      # Rendu Streamlit : sidebar, images, palette, tableau, graphique
├── styles.py               # CSS global + CSS iframe
├── .streamlit/config.toml  # Thème océan Streamlit
├── requirements.txt        # Dépendances Python
└── DOCUMENTATION.md        # Ce document
```

### 5.2 Description des modules

| Module | Responsabilité |
|---|---|
| `app.py` | Configure la page, injecte le CSS, gère l'upload, les onglets Retouche/Analyse et le cycle de session. |
| `constants.py` | `REFERENCE_COLORS` (67 couleurs), formats acceptés, teintes, filtres, bornes `K_MIN=2`, `K_MAX=8`, `K_MANUAL_MAX=12`, `MAX_SAMPLES=30000`, `RANDOM_STATE=42`. |
| `models.py` | `ColorResult` (rang, nom, rgb, hex, pixels, proportion, ΔE) et `AnalysisMetadata` (dimensions, mode, K, silhouette). |
| `ImageProcessor` | `load_image` (PIL → RGB, `thumbnail` conservant le ratio), `sample_pixels` (tirage sans remise), `rebuild_image_from_labels` (mapping labels → couleurs). |
| `ImageEditor` | Applique dans un ordre déterminé 27 réglages : noir & blanc, sépia, filtres artistiques, canaux, température, teinte, vibrance, saturation, ombres/hautes lumières, exposition, gamma, luminosité, contraste, netteté, flou gaussien, grain, postérisation, solarisation, seuil, vignette, pixelisation, teinte colorée, négatif. |
| `HistogramProcessor` | Luminance perceptuelle, histogramme luminance (64 bins) et canaux, comparaison avant/après, statistiques tonales. |
| `ColorProcessor` | `rgb2lab` / `lab2rgb` (scikit-image), `rgb_to_hex`, `get_color_name` (plus proche voisin LAB). |
| `ClusteringService` | `choose_best_k` (silhouette sur K ∈ [2,8]), `fit` (KMeans, `n_init=10`), `predict`. |
| `ColorAnalyzer` | Enchaîne les 16 étapes du pipeline et construit les objets de résultat. |
| `ResultRenderer` | Rendu Streamlit : sidebar, hero, cartes de métriques, palette avec copie HEX, graphique Altair, tableau, exports. |

### 5.3 Cycle de vie de l'application

1. **Session initiale** — pas d'image : écran vide avec consigne de téléversement.
2. **Upload** — les octets sont conservés dans `st.session_state["uploaded_bytes"]` pour éviter un re-téléversement.
3. **Retouche en temps réel** — chaque réglage de la sidebar déclenche `ImageEditor.apply()` et régénère les histogrammes avant/après.
4. **Analyse** — au clic sur le bouton, `ColorAnalyzer.analyze()` est exécuté ; les résultats sont stockés dans `st.session_state` (image, image segmentée, couleurs, métadonnées).
5. **Rendu** — palette, graphique des proportions, tableau, exports JSON/CSV.

---

## 6. Modèles mathématiques

### 6.1 Espace colorimétrique CIELAB

CIELAB est un espace perceptuellement quasi-uniforme : une différence de valeur y correspond environ à la même différence perçue, quelle que soit la région de l'espace.

- **L*** : clarté, L\* ∈ [0, 100] (noir → blanc) ;
- **a*** : axe vert → rouge, a\* ∈ [−128, 127] ;
- **b*** : axe bleu → jaune, b\* ∈ [−128, 127].

La distance euclidienne dans LAB définit la **différence de couleur ΔE** :

$$\Delta E = \sqrt{(\Delta L^*)^2 + (\Delta a^*)^2 + (\Delta b^*)^2}$$

C'est cette propriété qui justifie le choix de LAB pour le clustering et le nommage des couleurs.

### 6.2 Conversion RGB → LAB

La conversion passe par l'espace intermédiaire **CIE XYZ**.

**Étape 1 — linéarisation sRGB.** Pour chaque canal $c \in [0, 1]$ :

$$
c' = \begin{cases}
\dfrac{c}{12.92} & \text{si } c \le 0.04045 \\[6pt]
\left(\dfrac{c + 0.055}{1.055}\right)^{2.4} & \text{sinon}
\end{cases}
$$

**Étape 2 — passage sRGB linéaire → XYZ.** Matrice du blanc D65 :

$$
\begin{bmatrix} X \\ Y \\ Z \end{bmatrix}
= \begin{bmatrix}
0.4124564 & 0.3575761 & 0.1804375 \\
0.2126729 & 0.7151522 & 0.0721750 \\
0.0193339 & 0.1191920 & 0.9503041
\end{bmatrix}
\begin{bmatrix} R' \\ G' \\ B' \end{bmatrix}
$$

**Étape 3 — normalisation au blanc de référence** ($X_n=0.95047$, $Y_n=1.0$, $Z_n=1.08883$) et application de la fonction de transfert :

$$
f(t) = \begin{cases}
t^{1/3} & \text{si } t > \left(\frac{6}{29}\right)^3 \\[6pt]
\dfrac{1}{3}\left(\frac{29}{6}\right)^2 t + \dfrac{4}{29} & \text{sinon}
\end{cases}
$$

**Étape 4 — obtention de L\*a\*b\* :**

$$
L^* = 116\, f\!\left(\frac{Y}{Y_n}\right) - 16
\qquad
a^* = 500 \left[ f\!\left(\frac{X}{X_n}\right) - f\!\left(\frac{Y}{Y_n}\right) \right]
\qquad
b^* = 200 \left[ f\!\left(\frac{Y}{Y_n}\right) - f\!\left(\frac{Z}{Z_n}\right) \right]
$$

La conversion inverse **LAB → RGB** (utilisée pour les centres de clusters) applique les transformations inverses, le tout implémenté par scikit-image (`rgb2lab`, `lab2rgb`).

### 6.3 Luminance perceptuelle (Rec. 601)

La luminance de chaque pixel pondère les canaux selon la sensibilité de l'œil (vert dominant) :

$$
Y = 0.299\,R + 0.587\,G + 0.114\,B, \qquad Y \in [0, 255]
$$

Cette formule est utilisée par `HistogramProcessor` et par la retouche (ombres, hautes lumières, seuil).

### 6.4 Échantillonnage aléatoire des pixels

Pour accélérer l'entraînement de KMeans, un sous-ensemble de $S = 30\,000$ pixels est tiré **sans remise** selon une loi uniforme, à graine fixe :

$$
\mathcal{S} = \{ X_{i_j} \}_{j=1}^{S}, \qquad i_j \sim \mathcal{U}\{1, N\} \text{ sans remise}
$$

avec $N = H \times W$ le nombre total de pixels. Le clustering est appris sur $\mathcal{S}$ puis appliqué à la totalité des pixels (prédiction).

### 6.5 Clustering KMeans

**Objectif.** Partitionner les $N$ pixels $\{x_1, \dots, x_N\} \subset \mathbb{R}^3$ (coordonnées LAB) en $K$ clusters $C_1, \dots, C_K$ de centres $\mu_1, \dots, \mu_K$, en minimisant l'inertie intra-cluster (somme des carrés intra-cluster, WCSS) :

$$
J = \sum_{i=1}^{K} \sum_{x \in C_i} \lVert x - \mu_i \rVert_2^2
$$

**Algorithme** (alternance de deux étapes jusqu'à convergence, au plus `n_init = 10` initialisations, meilleure inertie retenue) :

1. **Initialisation** k-means++ (défaut scikit-learn), graine fixe $= 42$ ;
2. **Affectation** : chaque pixel est assigné au centre le plus proche :

$$
C_i^{(t)} = \left\{ x : \lVert x - \mu_i^{(t)} \rVert_2 = \min_{j} \lVert x - \mu_j^{(t)} \rVert_2 \right\}
$$

3. **Mise à jour** : chaque centre devient le barycentre de son cluster :

$$
\mu_i^{(t+1)} = \frac{1}{\lvert C_i^{(t)} \rvert} \sum_{x \in C_i^{(t)}} x
$$

### 6.6 Choix automatique de K — score de silhouette

Le **score de silhouette** mesure la cohésion d'un pixel avec son propre cluster (distance intra $a_i$) relativement à la distance au cluster voisin le plus proche ($b_i$) :

$$
s(i) = \frac{b(i) - a(i)}{\max(a(i), b(i))}, \qquad s(i) \in [-1, 1]
$$

- $s(i) \approx 1$ : pixel très bien classé ;
- $s(i) \approx 0$ : pixel à la frontière de deux clusters ;
- $s(i) < 0$ : pixel probablement mal affecté.

Le score global est la moyenne sur tous les pixels :

$$
\bar{s} = \frac{1}{N}\sum_{i=1}^{N} s(i)
$$

**Stratégie** : pour chaque $K \in [2, 8]$, entraîner KMeans, calculer $\bar{s}$ sur un échantillon de 5 000 pixels, et retenir $K^* = \arg\max_K \bar{s}$.

### 6.7 Calcul des proportions

Après prédiction, le nombre de pixels de chaque cluster $n_j$ est compté (`np.bincount`), et la proportion est :

$$
p_j = \frac{n_j}{\sum_{k=1}^{K} n_k}, \qquad \sum_j p_j = 1
$$

Les couleurs sont ensuite classées par proportion décroissante (rang 1 = couleur la plus présente).

### 6.8 Nommage des couleurs — distance ΔE

Chaque centre de cluster $L_c = (L^*, a^*, b^*)$ est comparé aux 67 couleurs de référence $R_k$ (converties au préalable en LAB) par distance euclidienne :

$$
k^* = \arg\min_k \lVert L_c - R_k \rVert_2
$$

Le nom retenu est celui de la couleur de référence la plus proche, et la valeur $\lVert L_c - R_{k^*} \rVert_2$ est stockée dans `distance_lab` comme indicateur de confiance.

### 6.9 Histogramme de luminance et statistiques tonales

**Histogramme.** L'intervalle $[0, 255]$ est découpé en $B = 64$ tranches de largeur $\Delta = 255 / 64$. Pour la tranche $j$ de bornes $[e_j, e_{j+1}]$ :

$$
h_j = \sum_{x} \mathbb{1}\{ e_j \le Y(x) < e_{j+1} \}
$$

**Zones tonales** (seuils : ombres ≤ 85, hautes lumières ≥ 170) :

- Ombres : $[0, 85)$ ;
- Tons moyens : $[85, 170)$ ;
- Hautes lumières : $[170, 255]$.

Le pourcentage de pixels par zone est $100 \times \mathbb{E}[\mathbb{1}\{Y \in \text{zone}\}]$.

**Statistiques** : moyenne $\mu = \frac{1}{N}\sum Y_i$, médiane, écart-type $\sigma$ (indicateur de contraste), min, max — calculées sur la luminance et sur chaque canal RGB.

### 6.10 Modèles de retouche d'image

Les opérations élémentaires de `ImageEditor` sont les suivantes :

**Exposition (EV)** — chaque +1 EV double la luminosité :

$$
I' = I \cdot 2^{EV}
$$

**Gamma** — correction de courbe :

$$
I' = 255 \left( \frac{I}{255} \right)^{1/\gamma}
$$

**Sépia** — combinaison linéaire des canaux :

$$
\begin{bmatrix} R' \\ G' \\ B' \end{bmatrix}
= \begin{bmatrix}
0.393 & 0.769 & 0.189 \\
0.349 & 0.686 & 0.168 \\
0.272 & 0.534 & 0.131
\end{bmatrix}
\begin{bmatrix} R \\ G \\ B \end{bmatrix}
$$

**Température** — décalage additif (chaud : +R, −B ; froid : inverse) :

$$
R' = R + \frac{t}{100}\cdot 45, \quad
G' = G + \frac{t}{100}\cdot 12, \quad
B' = B - \frac{t}{100}\cdot 45
$$

**Canaux (gains)** — $I'_c = I_c + g_c \cdot 1.275$ (facteur d'échelle du curseur).

**Vibrance** (espace HSV) — renforce surtout les couleurs ternes :

$$
S' = \begin{cases}
S + v\,(255 - S)\cdot 0.7 & \text{si } v \ge 0 \quad (v = \text{vibrance}/100) \\
S\,(1 + v) & \text{si } v < 0
\end{cases}
$$

**Rotation de teinte** — $H' = (H + \text{offset}) \bmod 256$.

**Ombres** — pondération forte sur les zones sombres ($w = (1 - Y/255)^2$) :

$$
I' = I + \frac{s}{100}\cdot w \cdot 120
$$

**Hautes lumières** — pondération forte sur les zones claires ($w = (Y/255)^2$) :

$$
I' = I + \frac{h}{100}\cdot w \cdot 120
$$

**Vignette** — facteur radial décroissant depuis le centre ($d$ distance normalisée, $d \in [0, 1]$) :

$$
d = \sqrt{\left(\frac{x - W/2}{W}\right)^2 + \left(\frac{y - H/2}{H}\right)^2} \Big/ 0.7071, \qquad
f = 1 - \frac{v}{100}\, d^2, \qquad I' = I \cdot f
$$

**Postérisation** — quantification à $L$ niveaux par canal :

$$
I' = \frac{\text{round}(I \cdot \frac{L-1}{255})}{(L-1)/255}
$$

**Solarisation** (effet Sabattier) — inversion au-delà d'un seuil $t$ :

$$
I' = \begin{cases}
I & \text{si } I < t \\
255 - I & \text{si } I \ge t
\end{cases}
$$

**Seuil** (noir & blanc) :

$$
I' = \begin{cases}
255 & \text{si } Y \ge t \\
0 & \text{sinon}
\end{cases}
$$

**Grain de film** — bruit gaussien additif : $I' = I + \mathcal{N}(0, \sigma)$, $\sigma = \frac{\text{grain}}{100}\cdot 50$.

**Teinte colorée** — interpolation entre l'image et une couleur cible $C$ :

$$
I' = I\,(1 - t) + C\,t, \qquad t = \frac{\text{intensité}}{100}
$$

**Négatif** — $I' = 255 - I$.

**Luminosité, contraste, saturation, netteté** — mises à l'échelle linéaire par `ImageEnhance` (facteur $= \text{valeur}/100$).

**Pixelisation** — réduction puis agrandissement avec filtre au plus proche voisin.

Toutes les opérations sont suivies d'un **clip** $\text{clip}(I, 0, 255)$ et d'un cast `uint8`.

---

## 7. Pipeline d'analyse

Le pipeline complet exécuté par `ColorAnalyzer.analyze()` :

```
Image RGB (H, W, 3)
   │  1. Conversion RGB → LAB
   ▼
Image LAB (H, W, 3)
   │  2. Aplatissement → pixels (H·W, 3)
   │  3. Échantillonnage (≤ 30 000 px, graine 42)
   ▼
Pixels LAB échantillonnés
   │  4. K automatique (silhouette, K∈[2,8]) OU K manuel
   │  5. KMeans (n_init=10) + prédiction sur tous les pixels
   ▼
Labels (H·W,)
   │  6. Comptage (bincount) → proportions
   │  7. Centres LAB → RGB
   │  8. Reconstruction image segmentée (H, W, 3)
   │  9. Tri par proportion décroissante
   │  10. Nommage (ΔE) + HEX + ColorResult
   ▼
Résultats : couleurs, image segmentée, métadonnées
```

---

## 8. Interface utilisateur

- **Thème océan** personnalisé (`.streamlit/config.toml`) : sarcelle `#137C8B`, ardoise `#344D59`, fond bleuté `#E8F1F3` ;
- **Hero** avec dégradé et badges récapitulatifs ;
- **CSS centralisé** (`styles.py`) : cartes de métriques, cadres d'images, palette avec rang, survol, copie des codes HEX au clic ;
- **Barre latérale** organisée en sections repliables : luminosité, tons, détail, effets avancés, filtres artistiques, paramètres d'analyse ;
- **Onglet Retouche** : comparaison avant/après + histogrammes luminance (zones ombres / tons moyens / hautes lumières) et canaux RGB superposés, statistiques comparatives mises à jour en direct ;
- **Onglet Analyse** : image segmentée, palette de couleurs, graphique des proportions coloré (Altair), tableau détaillé, exports JSON/CSV.

---

## 9. Exports de données

- **JSON** : liste des `ColorResult` (rang, nom, rgb, hex, pixels, proportion, proportion_pct, distance_lab) + `AnalysisMetadata` ;
- **CSV** : tableau des couleurs avec colonnes renommées et formatées.

---

## 10. Complexité et performances

| Opération | Complexité | Notes |
|---|---|---|
| Échantillonnage | $O(N)$ | $N \le W \times H$, borné à 30 000 px pour l'entraînement |
| KMeans | $O(K \cdot n \cdot d \cdot \text{iter} \cdot n\_init)$ | $n = 30\,000$, $d = 3$, $n\_init = 10$, au plus 7 valeurs de K ($K \in [2, 8]$) |
| Score silhouette | $O(n^2)$ en théorie | borné par échantillonnage à 5 000 px |
| Prédiction | $O(N \cdot K \cdot d)$ | $N$ = tous les pixels de l'image redimensionnée |
| Reconstruction | $O(N)$ | tableaux indexés NumPy |

Le redimensionnement (taille max 600 px par défaut, réglable jusqu'à 1 000 px) garantit un temps de réponse interactif dans Streamlit.

---

## 11. Limites connues

- **Nommage approximatif** : le nom dépend du dictionnaire de 67 références ; deux nuances proches peuvent recevoir le même nom, et le seuil de ΔE n'est pas discriminé (une couleur hors-gamme est toujours nommée).
- **KMeans sensible à l'initialisation** : atténué par `n_init=10` et la graine fixe ; les clusters sont convexes (forme sphérique), ce qui peut mal séparer des couleurs non linéairement séparables.
- **Choix de K par silhouette** : limité à [2, 8] ; le score peut favoriser K faible pour des images très hétérogènes.
- **Précision des conversions** : LAB → RGB peut produire des valeurs hors gamme, gérées par `clip` (légère perte de fidélité).
- **Redimensionnement** : l'analyse porte sur une image réduite, les pixels fins peuvent être perdus.

---

## 12. Conclusion

ImageSense combine des concepts mathématiques éprouvés — espace perceptuel CIELAB, clustering KMeans, score de silhouette, distance ΔE — dans une application web interactive et professionnelle. L'architecture modulaire (injection de dépendances) facilite l'extension : nouveaux espaces colorimétriques (HSV, HSL), clustering hiérarchique ou DBSCAN, seuillage de ΔE pour le nommage, ou analyse par régions constituent les pistes d'évolution naturelles.
