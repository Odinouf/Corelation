# Design : Corrélation Prix Baril / Prix Pompe France

## Objectif

Analyser la corrélation entre le prix du baril de pétrole brut et les prix des carburants à la pompe en France pour mettre en évidence les relations (ou absence) entre leurs hausses et baisses.

## Contexte

- **Usage :** Personnel
- **Période d'analyse :** 2020-2026 (incluant COVID et guerre en Ukraine)
- **Carburants analysés :**
  - Diesel (gazole)
  - Essence (SP95/E10)
  - Fioul domestique

## Architecture

### Structure des fichiers

```
Corelation/
├── shell.nix           # Environnement NixOS
├── analyse_petrole.py  # Script principal
└── resultats/          # Graphiques générés
    ├── evolution_temporelle.png
    ├── prix_normalises.png
    ├── correlations.png
    └── correlation_decalée.png
```

### Script monobloc

Le fichier `analyse_petrole.py` est organisé en sections :

1. **Configuration** — Dates, paramètres, clés API
2. **Récupération données** — Appels FRED + INSEE
3. **Traitement** — Nettoyage, alignement temporel
4. **Analyse** — Corrélations, délais
5. **Visualisation** — Graphiques matplotlib
6. **Main** — Orchestration

## Sources de données

| Donnée | Source | Fréquence |
|--------|--------|-----------|
| Prix baril Brent | FRED API | Quotidien |
| Prix carburants France | INSEE API | Quotidien/Hebdo |

### APIs

- **FRED** : Pas de clé requise (limite generous), ou clé gratuite pour plus de requêtes
- **INSEE** : Inscription requise pour clé API (gratuite)

## Flux de traitement

```
Récupération
├── FRED API → Prix baril Brent (quotidien)
└── INSEE API → Prix carburants France

Traitement
├── Nettoyage (valeurs manquantes, outliers)
├── Agrégation temporelle (alignement dates)
└── Calcul variation % (jour/semaine/mois)

Analyse
├── Corrélation Pearson (baril vs chaque carburant)
├── Corrélation décalée (baril t → carburant t+n jours)
└── Détection hausses/baisses significatives

Visualisation
├── Graphique multi-courbes
├── Heatmap corrélations
└── Graphique délai optimal
```

## Visualisations

4 graphiques PNG générés :

1. **Évolution temporelle** — Prix baril + 3 carburants (axes dual Y)
2. **Prix normalisés** — Base 100 au début pour comparer amplitudes
3. **Corrélations** — Scatter plots avec coefficient R²
4. **Corrélation décalée** — Délai optimal de répercussion

## Environnement technique

### NixOS

```nix
{ pkgs ? import <nixpkgs> {} }:
pkgs.mkShell {
  packages = [
    (pkgs.python3.withPackages (p: [
      p.pandas
      p.matplotlib
      p.requests
    ]))
  ];
}
```

### Exécution

```bash
nix-shell
python analyse_petrole.py
```

## Gestion des erreurs

- API indisponible → Message clair, pas de crash
- Données manquantes → Interpolation linéaire si trou < 7 jours
- Quotas API → Avertissement si limite approchée
- Données obsolètes → Alerte si dernières données > 30 jours

## Dépendances

- `pandas` — Manipulation données
- `matplotlib` — Graphiques
- `requests` — Appels API

## Livrables

- `shell.nix` — Environnement reproductible
- `analyse_petrole.py` — Script complet
- `resultats/*.png` — 4 graphiques d'analyse
