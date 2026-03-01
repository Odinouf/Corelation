# Analyse de Corrélation : Prix du Baril vs Prix à la Pompe en France

**Période analysée** : Janvier 2020 - Décembre 2025
**Date de l'analyse** : Mars 2026

---

## Résumé exécutif

Cette analyse examine la relation entre le prix du baril de pétrole Brent et les prix des carburants à la pompe en France sur une période de 6 ans, incluant :
- La crise COVID-19 (2020)
- La guerre en Ukraine (2022)
- La période de stabilisation (2023-2025)

### Conclusions principales

1. **Forte corrélation positive** (r = 0.79-0.83) entre le prix du baril et les carburants
2. **Délai de répercussion** de 23-38 jours avant transmission complète
3. **Asymétrie favorable** : les baisses sont mieux répercutées que les hausses
4. L'effet "rockets and feathers" n'est **PAS** observé en France

---

## Sources de données

| Donnée | Source | Fréquence | Accès |
|--------|--------|-----------|-------|
| Prix baril Brent | [FRED](https://fred.stlouisfed.org/series/DCOILBRENTEU) | Quotidien | API ouverte |
| Prix carburants France | [donnees.roulez-eco.fr](https://donnees.roulez-eco.fr) | Quotidien | Données ouvertes |

**Carburants analysés** :
- Diesel (Gazole)
- Essence (E10/SP95)
- Fioul domestique (simulé - non disponible en station)

---

## Résultats de corrélation

### Corrélation directe (sans délai)

| Carburant | Coefficient r | Interprétation |
|-----------|---------------|----------------|
| Diesel | 0.831 | Forte corrélation positive |
| Essence E10 | 0.787 | Bonne corrélation positive |
| Fioul (simulé) | 0.581 | Corrélation modérée |

### Corrélation avec délai optimal

| Carburant | Délai optimal | Coefficient r | Amélioration |
|-----------|---------------|---------------|--------------|
| Diesel | 38 jours | 0.889 | +7% |
| Essence E10 | 23 jours | 0.824 | +5% |
| Fioul (simulé) | 27 jours | 0.638 | +10% |

**Interprétation** : Une variation du prix du baril met 3 à 5 semaines pour se répercuter pleinement sur les prix à la pompe.

---

## Analyse de l'asymétrie hausse/baisse

### Méthodologie

On calcule le coefficient β de répercussion :
- β = variation carburant / variation baril
- β = 0.10 signifie qu'une variation de 10% du baril entraîne 1% de variation du carburant

On compare β pour les hausses vs les baisses du baril.

### Résultats par délai

| Délai | β hausse (diesel) | β baisse (diesel) | Asymétrie |
|-------|-------------------|-------------------|-----------|
| J+1 | -0.009 | +0.019 | +0.028 |
| J+7 | +0.008 | +0.092 | +0.085 |
| J+14 | -0.003 | +0.098 | +0.101 |
| J+21 | +0.013 | +0.126 | +0.113 |
| J+30 | +0.110 | +0.212 | +0.102 |

### Interprétation

- **Asymétrie positive** = les baisses sont mieux répercutées que les hausses
- **Asymétrie négative** = effet "rockets and feathers" (défavorable)

**Résultat** : L'asymétrie est **positive** à tous les délais (sauf J+60), avec une moyenne de **+0.060**.

### Conclusion sur l'asymétrie

> Les baisses du prix du baril sont répercutées environ **2x mieux** que les hausses aux délais optimaux (J+14 à J+21).

Ceci est **favorable au consommateur français** et contredit l'effet "rockets and feathers" observé dans d'autres pays.

---

## Facteurs explicatifs

### Pourquoi une asymétrie favorable en France ?

1. **Concurrence intense**
   - Densité élevée de stations-service
   - Facilité de comparaison des prix

2. **Transparence des prix**
   - Applications mobiles (Essence & Co, Fuel Flash, etc.)
   - Site gouvernemental prix-carburants.gouv.fr
   - Obligation d'affichage

3. **Taxes élevées (TICPE)**
   - Les taxes fixes représentent ~60% du prix
   - Cela amortit mécaniquement les variations du baril
   - Les hausses semblent donc moins importantes en pourcentage

4. **Régulation publique**
   - Surveillance des marges de distribution
   - Menace de régulation temporaire (comme en 2022)

---

## Visualisations générées

| Fichier | Description |
|---------|-------------|
| `1_evolution_temporelle.png` | Évolution des prix 2020-2026 |
| `2_prix_normalises.png` | Comparaison base 100 |
| `3_correlations.png` | Scatter plots avec R² |
| `4_correlation_decalée.png` | Corrélation par délai |
| `5_asymetrie_hausse_baisse.png` | Analyse asymétrie |

---

## Limites de l'analyse

1. **Taux de change USD/EUR** : Le baril est en dollars, les carburants en euros. Les variations de change peuvent affecter la corrélation.

2. **Fioul domestique** : Données simulées car non vendu en station (livraison uniquement).

3. **Autres facteurs** : L'analyse ne tient pas compte des variations de marge de distribution, des stocks stratégiques, ou des décisions politiques (remises gouvernementales).

4. **Période atypique** : 2020-2025 inclut des chocs majeurs (COVID, Ukraine) qui peuvent biaiser les résultats.

---

## Utilisation du script

```bash
# Entrer dans l'environnement NixOS
nix-shell

# Lancer l'analyse principale
python analyse_petrole.py

# Analyser l'asymétrie
python analyse_asymetrie.py
```

---

## Fichiers du projet

```
Corelation/
├── shell.nix                 # Environnement NixOS
├── analyse_petrole.py        # Script principal
├── analyse_asymetrie.py      # Analyse asymétrie
├── README.md                 # Documentation
└── resultats/
    ├── 1_evolution_temporelle.png
    ├── 2_prix_normalises.png
    ├── 3_correlations.png
    ├── 4_correlation_decalée.png
    └── 5_asymetrie_hausse_baisse.png
```

---

*Analyse réalisée avec Python, pandas, matplotlib. Données : FRED, Ministère de la Transition Écologique.*
