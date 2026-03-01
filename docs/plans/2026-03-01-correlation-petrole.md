# Corrélation Pétrole Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Créer un script Python qui analyse la corrélation entre le prix du baril Brent et les prix des carburants à la pompe en France (2020-2026).

**Architecture:** Script monobloc avec sections pour la récupération API (FRED + INSEE), le traitement des données, l'analyse des corrélations, et la génération de 4 graphiques matplotlib. Environnement NixOS via shell.nix.

**Tech Stack:** Python 3, pandas, matplotlib, requests, NixOS (nix-shell)

---

## Task 1: Créer l'environnement NixOS

**Files:**
- Create: `shell.nix`

**Step 1: Créer shell.nix**

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

  shellHook = ''
    echo "Environnement prêt pour l'analyse pétrole"
    echo "Lancer: python analyse_petrole.py"
  '';
}
```

**Step 2: Vérifier que nix-shell fonctionne**

Run: `nix-shell --run "python --version"`
Expected: `Python 3.x.x`

**Step 3: Commit**

```bash
git add shell.nix
git commit -m "chore: add nix-shell environment with pandas, matplotlib, requests"
```

---

## Task 2: Créer la structure du script et la configuration

**Files:**
- Create: `analyse_petrole.py`

**Step 1: Créer le squelette du script avec configuration**

```python
#!/usr/bin/env python3
"""
Analyse de corrélation entre le prix du baril de pétrole Brent
et les prix des carburants à la pompe en France.
"""

import os
from datetime import datetime
from dataclasses import dataclass

# ============================================================================
# CONFIGURATION
# ============================================================================

@dataclass
class Config:
    """Configuration de l'analyse."""
    # Période d'analyse
    start_date: str = "2020-01-01"
    end_date: str = "2026-03-01"

    # API FRED (prix baril Brent)
    fred_series_id: str = "DCOILBRENTEU"  # Brent Crude Oil Price
    fred_api_key: str = ""  # Vide = mode anonyme (limite généreuse)

    # API INSEE (prix carburants France)
    insee_api_key: str = ""  # À remplir par l'utilisateur

    # Carburants à analyser (codes série INSEE)
    carburants: dict = None

    # Sortie
    output_dir: str = "resultats"

    def __post_init__(self):
        if self.carburants is None:
            self.carburants = {
                "diesel": "000872574",      # Gazole
                "essence_sp95": "000872573", # SP95
                "fioul": "000872575",        # Fioul domestique
            }


# ============================================================================
# RÉCUPÉRATION DES DONNÉES
# ============================================================================

def fetch_fred_data(config: Config) -> dict:
    """Récupère les prix du baril Brent depuis FRED."""
    pass


def fetch_insee_data(config: Config) -> dict:
    """Récupère les prix des carburants depuis l'INSEE."""
    pass


# ============================================================================
# TRAITEMENT DES DONNÉES
# ============================================================================

def clean_and_align_data(baril_data: dict, carburants_data: dict) -> dict:
    """Nettoie et aligne temporellement les données."""
    pass


# ============================================================================
# ANALYSE
# ============================================================================

def calculate_correlations(aligned_data: dict) -> dict:
    """Calcule les corrélations baril vs carburants."""
    pass


def calculate_lagged_correlations(aligned_data: dict, max_lag: int = 60) -> dict:
    """Calcule les corrélations avec délai (0 à max_lag jours)."""
    pass


# ============================================================================
# VISUALISATION
# ============================================================================

def plot_evolution_temporelle(aligned_data: dict, config: Config):
    """Génère le graphique d'évolution temporelle."""
    pass


def plot_prix_normalises(aligned_data: dict, config: Config):
    """Génère le graphique des prix normalisés (base 100)."""
    pass


def plot_correlations(correlations: dict, aligned_data: dict, config: Config):
    """Génère les scatter plots de corrélation."""
    pass


def plot_correlation_decalée(lagged_corr: dict, config: Config):
    """Génère le graphique de corrélation décalée."""
    pass


# ============================================================================
# MAIN
# ============================================================================

def main():
    """Point d'entrée principal."""
    config = Config()

    # Créer le dossier de sortie
    os.makedirs(config.output_dir, exist_ok=True)

    print("=" * 60)
    print("ANALYSE CORRÉLATION PÉTROLE - FRANCE")
    print("=" * 60)

    # 1. Récupération
    print("\n[1/5] Récupération données FRED (baril Brent)...")
    baril_data = fetch_fred_data(config)

    print("[1/5] Récupération données INSEE (carburants France)...")
    carburants_data = fetch_insee_data(config)

    # 2. Traitement
    print("\n[2/5] Nettoyage et alignement des données...")
    aligned_data = clean_and_align_data(baril_data, carburants_data)

    # 3. Analyse
    print("\n[3/5] Calcul des corrélations...")
    correlations = calculate_correlations(aligned_data)

    print("[3/5] Calcul des corrélations décalées...")
    lagged_corr = calculate_lagged_correlations(aligned_data)

    # 4. Visualisation
    print("\n[4/5] Génération des graphiques...")
    plot_evolution_temporelle(aligned_data, config)
    plot_prix_normalises(aligned_data, config)
    plot_correlations(correlations, aligned_data, config)
    plot_correlation_decalée(lagged_corr, config)

    # 5. Résumé
    print("\n[5/5] Résumé des corrélations:")
    print("-" * 40)
    for name, corr in correlations.items():
        print(f"  {name}: r = {corr:.3f}")

    print(f"\nGraphiques sauvegardés dans '{config.output_dir}/'")
    print("=" * 60)


if __name__ == "__main__":
    main()
```

**Step 2: Vérifier la syntaxe**

Run: `nix-shell --run "python -m py_compile analyse_petrole.py"`
Expected: Pas d'erreur

**Step 3: Commit**

```bash
git add analyse_petrole.py
git commit -m "feat: add script skeleton with configuration and function stubs"
```

---

## Task 3: Implémenter la récupération FRED

**Files:**
- Modify: `analyse_petrole.py` (section RÉCUPÉRATION)

**Step 1: Ajouter les imports nécessaires**

Ajouter au début du fichier, après `import os`:

```python
import requests
import pandas as pd
from typing import Optional
```

**Step 2: Implémenter fetch_fred_data**

Remplacer la fonction `fetch_fred_data` par:

```python
def fetch_fred_data(config: Config) -> dict:
    """Récupère les prix du baril Brent depuis FRED.

    Returns:
        dict avec 'dates' et 'values'
    """
    base_url = "https://fred.stlouisfed.org/graph/freddata.csv"

    params = {
        "id": config.fred_series_id,
        "cosd": config.start_date,
        "coed": config.end_date,
    }

    # Ajouter clé API si disponible
    if config.fred_api_key:
        params["api_key"] = config.fred_api_key

    try:
        response = requests.get(base_url, params=params, timeout=30)
        response.raise_for_status()

        # Parser le CSV (format: date, valeur)
        lines = response.text.strip().split('\n')

        dates = []
        values = []

        for line in lines[1:]:  # Skip header
            parts = line.split(',')
            if len(parts) >= 2 and parts[1] != '.':  # '.' = valeur manquante
                dates.append(parts[0])
                try:
                    values.append(float(parts[1]))
                except ValueError:
                    continue

        print(f"  → {len(values)} points récupérés (baril Brent)")

        return {"dates": dates, "values": values}

    except requests.RequestException as e:
        print(f"  ✗ Erreur FRED: {e}")
        return {"dates": [], "values": []}
```

**Step 3: Tester la récupération FRED**

Ajouter un test temporaire dans main() après la création de config:

```python
# Test FRED
baril = fetch_fred_data(config)
print(f"Test FRED: {len(baril['values'])} valeurs")
if baril['values']:
    print(f"  Dernier prix: ${baril['values'][-1]:.2f}")
```

Run: `nix-shell --run "python analyse_petrole.py"`
Expected: Affiche le nombre de points et le dernier prix du baril

**Step 4: Commit**

```bash
git add analyse_petrole.py
git commit -m "feat: implement FRED API data fetching for Brent oil prices"
```

---

## Task 4: Implémenter la récupération INSEE

**Files:**
- Modify: `analyse_petrole.py` (section RÉCUPÉRATION)

**Step 1: Implémenter fetch_insee_data**

Remplacer la fonction `fetch_insee_data` par:

```python
def fetch_insee_data(config: Config) -> dict:
    """Récupère les prix des carburants depuis l'INSEE.

    Note: L'INSEE requiert une clé API. Si non fournie,
    utilise des données de démonstration.

    Returns:
        dict avec carburant -> {dates, values}
    """
    result = {}

    if not config.insee_api_key:
        print("  ⚠ Pas de clé API INSEE fournie")
        print("  → Utilisation de données de démonstration simulées")
        return _generate_demo_data(config)

    # API INSEE réelle
    base_url = "https://api.insee.fr/series/BDM/V1/data/SERIES_BDM"

    headers = {
        "Authorization": f"Bearer {config.insee_api_key}",
        "Accept": "application/json",
    }

    for name, series_id in config.carburants.items():
        try:
            params = {
                "idBank": series_id,
                "startPeriod": config.start_date.replace("-", ""),
                "endPeriod": config.end_date.replace("-", ""),
            }

            response = requests.get(
                base_url,
                headers=headers,
                params=params,
                timeout=30
            )
            response.raise_for_status()

            data = response.json()

            # Parser la réponse INSEE
            observations = data.get("series", [{}])[0].get("observations", [])
            dates = []
            values = []

            for obs in observations:
                dates.append(obs.get("period", ""))
                values.append(float(obs.get("value", 0)))

            result[name] = {"dates": dates, "values": values}
            print(f"  → {name}: {len(values)} points")

        except requests.RequestException as e:
            print(f"  ✗ Erreur INSEE pour {name}: {e}")
            result[name] = {"dates": [], "values": []}

    return result


def _generate_demo_data(config: Config) -> dict:
    """Génère des données de démonstration réalistes."""
    import random

    # Dates quotidiennes
    start = datetime.strptime(config.start_date, "%Y-%m-%d")
    end = datetime.strptime(config.end_date, "%Y-%m-%d")

    dates = []
    current = start
    while current <= end:
        dates.append(current.strftime("%Y-%m-%d"))
        current += pd.Timedelta(days=1)

    # Prix de base (€/litre) approximatifs 2024
    base_prices = {
        "diesel": 1.75,
        "essence_sp95": 1.85,
        "fioul": 0.95,
    }

    # Facteur de corrélation avec le baril (approximatif)
    correlation_factors = {
        "diesel": 0.008,      # ~0.8 centime par dollar de baril
        "essence_sp95": 0.009,
        "fioul": 0.007,
    }

    result = {}

    # Simuler un prix du baril de référence (pour la démo)
    baril_base = 80  # $/baril
    baril_trend = []

    for i, date in enumerate(dates):
        # Tendance avec variations
        noise = random.gauss(0, 3)
        spike = 30 if "2022-03" <= date <= "2022-08" else 0  # Guerre Ukraine
        covid_drop = -30 if "2020-04" <= date <= "2020-06" else 0

        price = baril_base + spike + covid_drop + noise
        baril_trend.append(max(20, price))  # Minimum $20

    # Générer prix carburants corrélés
    for name, base in base_prices.items():
        values = []
        factor = correlation_factors[name]

        for i, baril_price in enumerate(baril_trend):
            # Corrélation avec délai
            lag = min(i, 7)  # Délai ~1 semaine
            ref_baril = baril_trend[i - lag] if i >= lag else baril_price

            # Prix = base + (baril - 80) * facteur + bruit
            price = base + (ref_baril - 80) * factor + random.gauss(0, 0.02)
            values.append(round(max(0.5, price), 3))

        result[name] = {"dates": dates, "values": values}

    return result
```

**Step 2: Tester la récupération INSEE (mode démo)**

Run: `nix-shell --run "python analyse_petrole.py"`
Expected: Affiche "Utilisation de données de démonstration" et les compteurs

**Step 3: Nettoyer le test temporaire de main()**

Supprimer les lignes de test ajoutées dans Task 3 Step 3.

**Step 4: Commit**

```bash
git add analyse_petrole.py
git commit -m "feat: implement INSEE API with demo data fallback"
```

---

## Task 5: Implémenter le nettoyage et alignement des données

**Files:**
- Modify: `analyse_petrole.py` (section TRAITEMENT)

**Step 1: Implémenter clean_and_align_data**

Remplacer la fonction `clean_and_align_data` par:

```python
def clean_and_align_data(baril_data: dict, carburants_data: dict) -> dict:
    """Nettoie et aligne temporellement les données.

    Returns:
        dict avec DataFrame pandas pour chaque série, indexé par date
    """
    # Créer DataFrame pour le baril
    df_baril = pd.DataFrame({
        "date": pd.to_datetime(baril_data["dates"]),
        "baril": baril_data["values"],
    }).set_index("date").sort_index()

    # Supprimer les doublons et valeurs nulles
    df_baril = df_baril[~df_baril.index.duplicated(keep="first")]
    df_baril = df_baril.dropna()

    # Créer DataFrames pour chaque carburant
    carburant_dfs = {}
    for name, data in carburants_data.items():
        if not data["dates"]:
            continue

        df = pd.DataFrame({
            "date": pd.to_datetime(data["dates"]),
            name: data["values"],
        }).set_index("date").sort_index()

        df = df[~df.index.duplicated(keep="first")]
        df = df.dropna()

        carburant_dfs[name] = df

    # Trouver la période commune
    all_dfs = [df_baril] + list(carburant_dfs.values())
    start = max(df.index.min() for df in all_dfs)
    end = min(df.index.max() for df in all_dfs)

    print(f"  Période commune: {start.date()} à {end.date()}")

    # Rééchantillonner sur une base quotidienne et interpoler
    date_range = pd.date_range(start, end, freq="D")

    aligned = {"baril": df_baril.reindex(date_range)}

    # Interpolation linéaire pour les trous < 7 jours
    aligned["baril"] = aligned["baril"].interpolate(
        method="linear",
        limit=7
    )

    for name, df in carburant_dfs.items():
        aligned[name] = df.reindex(date_range).interpolate(method="linear", limit=7)

    # Supprimer les jours avec des données manquantes
    combined = pd.DataFrame({name: df.iloc[:, 0] for name, df in aligned.items()})
    combined = combined.dropna()

    print(f"  {len(combined)} jours avec données complètes")

    # Reconstruire le dict de DataFrames
    result = {}
    for col in combined.columns:
        result[col] = combined[[col]]
        result[col].columns = [col]

    return result
```

**Step 2: Tester l'alignement**

Ajouter temporairement dans main() après clean_and_align_data:

```python
# Test alignement
print(f"Colonnes alignées: {list(aligned_data.keys())}")
print(f"Échantillon baril:\n{aligned_data['baril'].head()}")
```

Run: `nix-shell --run "python analyse_petrole.py"`
Expected: Affiche la période commune et les colonnes

**Step 3: Nettoyer le test**

Supprimer les lignes de test.

**Step 4: Commit**

```bash
git add analyse_petrole.py
git commit -m "feat: implement data cleaning and temporal alignment"
```

---

## Task 6: Implémenter le calcul des corrélations

**Files:**
- Modify: `analyse_petrole.py` (section ANALYSE)

**Step 1: Implémenter calculate_correlations**

Remplacer la fonction `calculate_correlations` par:

```python
def calculate_correlations(aligned_data: dict) -> dict:
    """Calcule les corrélations Pearson entre le baril et chaque carburant.

    Returns:
        dict carburant -> coefficient de corrélation r
    """
    correlations = {}

    baril = aligned_data["baril"].iloc[:, 0]

    for name, df in aligned_data.items():
        if name == "baril":
            continue

        values = df.iloc[:, 0]

        # Corrélation de Pearson
        corr = baril.corr(values)
        correlations[name] = corr

        print(f"  {name}: r = {corr:.3f}")

    return correlations
```

**Step 2: Implémenter calculate_lagged_correlations**

Remplacer la fonction `calculate_lagged_correlations` par:

```python
def calculate_lagged_correlations(aligned_data: dict, max_lag: int = 60) -> dict:
    """Calcule les corrélations avec différents délais.

    Le délai optimal indique combien de jours s'écoulent avant
    qu'une variation du baril se répercute sur le prix à la pompe.

    Returns:
        dict carburant -> {lags: [...], correlations: [...], optimal_lag: N}
    """
    results = {}

    baril = aligned_data["baril"].iloc[:, 0]

    for name, df in aligned_data.items():
        if name == "baril":
            continue

        values = df.iloc[:, 0]
        lags = list(range(0, max_lag + 1))
        corrs = []

        for lag in lags:
            if lag == 0:
                shifted_baril = baril
            else:
                shifted_baril = baril.shift(lag)

            # Corrélation avec la série décalée
            corr = shifted_baril.corr(values)
            corrs.append(corr if not pd.isna(corr) else 0)

        # Trouver le délai optimal (corrélation maximale)
        optimal_idx = corrs.index(max(corrs))
        optimal_lag = lags[optimal_idx]

        results[name] = {
            "lags": lags,
            "correlations": corrs,
            "optimal_lag": optimal_lag,
            "optimal_correlation": corrs[optimal_idx],
        }

        print(f"  {name}: délai optimal = {optimal_lag} jours (r = {corrs[optimal_idx]:.3f})")

    return results
```

**Step 3: Tester les corrélations**

Run: `nix-shell --run "python analyse_petrole.py"`
Expected: Affiche les corrélations et délais optimaux

**Step 4: Commit**

```bash
git add analyse_petrole.py
git commit -m "feat: implement Pearson correlation and lagged correlation analysis"
```

---

## Task 7: Implémenter la visualisation - Évolution temporelle

**Files:**
- Modify: `analyse_petrole.py` (section VISUALISATION)

**Step 1: Ajouter les imports matplotlib**

Ajouter après les imports existants:

```python
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
```

**Step 2: Implémenter plot_evolution_temporelle**

Remplacer la fonction `plot_evolution_temporelle` par:

```python
def plot_evolution_temporelle(aligned_data: dict, config: Config):
    """Génère le graphique d'évolution temporelle avec axe dual Y."""
    fig, ax1 = plt.subplots(figsize=(14, 6))

    # Axe gauche: prix du baril ($)
    baril = aligned_data["baril"]
    ax1.plot(baril.index, baril.iloc[:, 0],
             color="black", linewidth=2, label="Baril Brent ($)")
    ax1.set_xlabel("Date")
    ax1.set_ylabel("Prix baril ($/baril)", color="black")
    ax1.tick_params(axis="y", labelcolor="black")

    # Axe droit: prix carburants (€)
    ax2 = ax1.twinx()
    colors = {
        "diesel": "#1f77b4",
        "essence_sp95": "#ff7f0e",
        "fioul": "#2ca02c",
    }

    for name, df in aligned_data.items():
        if name == "baril":
            continue

        color = colors.get(name, "gray")
        label = name.replace("_", " ").title()
        ax2.plot(df.index, df.iloc[:, 0],
                 color=color, linewidth=1.5, alpha=0.8, label=label)

    ax2.set_ylabel("Prix carburant (€/L)", color="gray")
    ax2.tick_params(axis="y", labelcolor="gray")

    # Formatage dates
    ax1.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
    ax1.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
    plt.xticks(rotation=45)

    # Légende combinée
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper left")

    plt.title("Évolution prix baril Brent vs carburants France (2020-2026)")
    plt.tight_layout()

    output_path = os.path.join(config.output_dir, "1_evolution_temporelle.png")
    plt.savefig(output_path, dpi=150)
    plt.close()

    print(f"  → {output_path}")
```

**Step 3: Tester le graphique**

Run: `nix-shell --run "python analyse_petrole.py"`
Expected: Fichier `resultats/1_evolution_temporelle.png` créé

**Step 4: Commit**

```bash
git add analyse_petrole.py
git commit -m "feat: add temporal evolution plot with dual Y-axis"
```

---

## Task 8: Implémenter la visualisation - Prix normalisés

**Files:**
- Modify: `analyse_petrole.py` (section VISUALISATION)

**Step 1: Implémenter plot_prix_normalises**

Remplacer la fonction `plot_prix_normalises` par:

```python
def plot_prix_normalises(aligned_data: dict, config: Config):
    """Génère le graphique des prix normalisés (base 100 au début)."""
    fig, ax = plt.subplots(figsize=(14, 6))

    # Normaliser toutes les séries à base 100
    normalized = {}

    for name, df in aligned_data.items():
        first_val = df.iloc[0, 0]
        if first_val > 0:
            normalized[name] = (df.iloc[:, 0] / first_val) * 100

    # Couleurs
    colors = {
        "baril": "black",
        "diesel": "#1f77b4",
        "essence_sp95": "#ff7f0e",
        "fioul": "#2ca02c",
    }

    # Tracer
    for name, series in normalized.items():
        color = colors.get(name, "gray")
        label = name.replace("_", " ").title()
        linewidth = 2.5 if name == "baril" else 1.5
        ax.plot(series.index, series.values,
                color=color, linewidth=linewidth, alpha=0.8, label=label)

    # Ligne de référence à 100
    ax.axhline(y=100, color="gray", linestyle="--", alpha=0.5)

    # Formatage
    ax.set_xlabel("Date")
    ax.set_ylabel("Prix normalisé (base 100)")
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
    plt.xticks(rotation=45)
    ax.legend(loc="upper left")
    ax.grid(True, alpha=0.3)

    plt.title("Prix normalisés - Comparaison des variations (base 100 = début période)")
    plt.tight_layout()

    output_path = os.path.join(config.output_dir, "2_prix_normalises.png")
    plt.savefig(output_path, dpi=150)
    plt.close()

    print(f"  → {output_path}")
```

**Step 2: Tester**

Run: `nix-shell --run "python analyse_petrole.py"`
Expected: Fichier `resultats/2_prix_normalises.png` créé

**Step 3: Commit**

```bash
git add analyse_petrole.py
git commit -m "feat: add normalized price comparison plot (base 100)"
```

---

## Task 9: Implémenter la visualisation - Scatter plots corrélation

**Files:**
- Modify: `analyse_petrole.py` (section VISUALISATION)

**Step 1: Implémenter plot_correlations**

Remplacer la fonction `plot_correlations` par:

```python
def plot_correlations(correlations: dict, aligned_data: dict, config: Config):
    """Génère les scatter plots de corrélation avec coefficients R²."""
    carburants = [k for k in aligned_data.keys() if k != "baril"]

    fig, axes = plt.subplots(1, len(carburants), figsize=(15, 5))
    if len(carburants) == 1:
        axes = [axes]

    baril = aligned_data["baril"].iloc[:, 0]

    colors = {
        "diesel": "#1f77b4",
        "essence_sp95": "#ff7f0e",
        "fioul": "#2ca02c",
    }

    for ax, name in zip(axes, carburants):
        values = aligned_data[name].iloc[:, 0]
        color = colors.get(name, "gray")

        # Scatter plot
        ax.scatter(baril, values, alpha=0.3, s=10, color=color)

        # Ligne de régression
        z = np.polyfit(baril, values, 1)
        p = np.poly1d(z)
        x_line = np.linspace(baril.min(), baril.max(), 100)
        ax.plot(x_line, p(x_line), "r--", linewidth=2, alpha=0.8)

        # Coefficient R²
        r = correlations.get(name, 0)
        r_squared = r ** 2

        ax.set_xlabel("Prix baril ($)")
        ax.set_ylabel("Prix (€/L)")
        ax.set_title(f"{name.replace('_', ' ').title()}\nr = {r:.3f}, R² = {r_squared:.3f}")
        ax.grid(True, alpha=0.3)

    plt.suptitle("Corrélations: Prix baril vs Prix carburants France", fontsize=14)
    plt.tight_layout()

    output_path = os.path.join(config.output_dir, "3_correlations.png")
    plt.savefig(output_path, dpi=150)
    plt.close()

    print(f"  → {output_path}")
```

**Step 2: Ajouter import numpy**

Ajouter après les imports matplotlib:

```python
import numpy as np
```

**Step 3: Tester**

Run: `nix-shell --run "python analyse_petrole.py"`
Expected: Fichier `resultats/3_correlations.png` créé

**Step 4: Commit**

```bash
git add analyse_petrole.py
git commit -m "feat: add correlation scatter plots with regression lines"
```

---

## Task 10: Implémenter la visualisation - Corrélation décalée

**Files:**
- Modify: `analyse_petrole.py` (section VISUALISATION)

**Step 1: Implémenter plot_correlation_decalée**

Remplacer la fonction `plot_correlation_decalée` par:

```python
def plot_correlation_decalée(lagged_corr: dict, config: Config):
    """Génère le graphique de corrélation en fonction du délai."""
    fig, ax = plt.subplots(figsize=(12, 6))

    colors = {
        "diesel": "#1f77b4",
        "essence_sp95": "#ff7f0e",
        "fioul": "#2ca02c",
    }

    for name, data in lagged_corr.items():
        color = colors.get(name, "gray")
        label = name.replace("_", " ").title()

        ax.plot(data["lags"], data["correlations"],
                color=color, linewidth=2, label=label)

        # Marquer le délai optimal
        opt_lag = data["optimal_lag"]
        opt_corr = data["optimal_correlation"]
        ax.scatter([opt_lag], [opt_corr],
                   color=color, s=100, zorder=5, marker="*")
        ax.annotate(
            f"{opt_lag}j",
            (opt_lag, opt_corr),
            textcoords="offset points",
            xytext=(5, 5),
            fontsize=10,
            color=color,
        )

    ax.set_xlabel("Délai (jours)")
    ax.set_ylabel("Corrélation (r)")
    ax.set_title("Corrélation baril → carburant selon le délai\n(étoile = délai optimal)")
    ax.legend(loc="lower right")
    ax.grid(True, alpha=0.3)
    ax.set_xlim(0, max(data["lags"][-1] for data in lagged_corr.values()))

    plt.tight_layout()

    output_path = os.path.join(config.output_dir, "4_correlation_decalée.png")
    plt.savefig(output_path, dpi=150)
    plt.close()

    print(f"  → {output_path}")
```

**Step 2: Tester le script complet**

Run: `nix-shell --run "python analyse_petrole.py"`
Expected: Les 4 graphiques générés, résumé des corrélations affiché

**Step 3: Commit**

```bash
git add analyse_petrole.py
git commit -m "feat: add lagged correlation plot showing optimal delay"
```

---

## Task 11: Finalisation et documentation

**Files:**
- Create: `README.md`

**Step 1: Créer le README**

```markdown
# Corrélation Pétrole - France

Analyse de la corrélation entre le prix du baril de pétrole Brent et les prix des carburants à la pompe en France.

## Utilisation

```bash
# Entrer dans l'environnement NixOS
nix-shell

# Lancer l'analyse
python analyse_petrole.py
```

## Résultats

4 graphiques générés dans `resultats/`:

1. **Évolution temporelle** - Prix baril et carburants sur 2020-2026
2. **Prix normalisés** - Comparaison des amplitudes (base 100)
3. **Corrélations** - Scatter plots avec coefficients R²
4. **Corrélation décalée** - Délai optimal de répercussion

## Sources de données

- **Baril Brent**: [FRED](https://fred.stlouisfed.org/series/DCOILBRENTEU)
- **Carburants France**: [INSEE](https://www.insee.fr)

### Clé API INSEE

Pour les données réelles, obtenez une clé gratuite sur https://api.insee.fr et ajoutez-la dans le script:

```python
insee_api_key: str = "VOTRE_CLE"
```

Sans clé, le script utilise des données simulées réalistes.

## Carburants analysés

- Diesel (gazole)
- Essence SP95
- Fioul domestique
```

**Step 2: Vérifier que tout fonctionne**

Run: `nix-shell --run "python analyse_petrole.py"`
Expected: Tous les graphiques générés sans erreur

**Step 3: Commit final**

```bash
git add README.md analyse_petrole.py
git commit -m "docs: add README with usage instructions"
```

---

## Résumé

| Task | Description | Fichier |
|------|-------------|---------|
| 1 | Environnement NixOS | `shell.nix` |
| 2 | Structure du script | `analyse_petrole.py` |
| 3 | API FRED | `analyse_petrole.py` |
| 4 | API INSEE | `analyse_petrole.py` |
| 5 | Nettoyage données | `analyse_petrole.py` |
| 6 | Calcul corrélations | `analyse_petrole.py` |
| 7 | Graphique évolution | `analyse_petrole.py` |
| 8 | Graphique normalisé | `analyse_petrole.py` |
| 9 | Scatter plots | `analyse_petrole.py` |
| 10 | Corrélation décalée | `analyse_petrole.py` |
| 11 | Documentation | `README.md` |
