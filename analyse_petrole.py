#!/usr/bin/env python3
"""
Analyse de corrélation entre le prix du baril de pétrole Brent
et les prix des carburants à la pompe en France.
"""

import os
import requests
import pandas as pd
from typing import Optional
from datetime import datetime
from dataclasses import dataclass
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import zipfile
import io
import xml.etree.ElementTree as ET
from collections import defaultdict

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

    # Source données carburants: donnees.roulez-eco.fr (Ministère Transition Écologique)
    # Pas de clé API requise

    # Carburants à analyser (noms XML dans donnees.roulez-eco.fr)
    carburants: dict = None

    # Sortie
    output_dir: str = "resultats"

    def __post_init__(self):
        if self.carburants is None:
            self.carburants = {
                "diesel": "Gazole",        # Gazole (diesel)
                "essence_sp95": "E10",     # SP95-E10 (essence principale)
                "fioul": None,             # Fioul non disponible en station
            }


# ============================================================================
# RÉCUPÉRATION DES DONNÉES
# ============================================================================

def fetch_fred_data(config: Config) -> dict:
    """Récupère les prix du baril Brent depuis FRED.

    Returns:
        dict avec 'dates' et 'values'
    """
    base_url = "https://fred.stlouisfed.org/graph/fredgraph.csv"

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


def fetch_fuel_prices(config: Config) -> dict:
    """Récupère les prix des carburants depuis donnees.roulez-eco.fr.

    Source: Ministère de la Transition Écologique (données ouvertes).
    Format: ZIP contenant XML avec prix par station.

    Returns:
        dict avec carburant -> {dates, values}
    """
    # Années à télécharger selon la période
    start_year = int(config.start_date[:4])
    end_year = int(config.end_date[:4])
    years = range(start_year, end_year + 1)

    # Agréger tous les prix par jour et carburant
    # Structure: {carburant: {date: [prix1, prix2, ...]}}
    all_prices = defaultdict(lambda: defaultdict(list))

    for year in years:
        print(f"    Téléchargement {year}...", end=" ", flush=True)
        try:
            url = f"https://donnees.roulez-eco.fr/opendata/annee/{year}"
            response = requests.get(url, timeout=60)
            response.raise_for_status()

            # Le ZIP est en mémoire
            with zipfile.ZipFile(io.BytesIO(response.content)) as zf:
                # Trouver le fichier XML dans le ZIP
                xml_files = [f for f in zf.namelist() if f.endswith('.xml')]
                if not xml_files:
                    print("pas de XML")
                    continue

                # Parser le XML
                with zf.open(xml_files[0]) as xml_file:
                    # Lire et décoder (ISO-8859-1 selon l'en-tête XML)
                    content = xml_file.read().decode('iso-8859-1')
                    root = ET.fromstring(content)

                    # Parcourir tous les prix
                    for pdv in root.findall('.//pdv'):
                        for prix in pdv.findall('prix'):
                            fuel_name = prix.get('nom')
                            maj = prix.get('maj')
                            value = prix.get('valeur')

                            if fuel_name and maj and value:
                                try:
                                    # Extraire juste la date (YYYY-MM-DD)
                                    date = maj[:10]
                                    price = float(value)

                                    # Format change en 2022:
                                    # - 2020-2021: millièmes d'euro → diviser par 1000
                                    # - 2022+: euros directement
                                    if year < 2022:
                                        price = price / 1000.0

                                    # Ignorer les valeurs aberrantes (< 0.5€ ou > 3€)
                                    if 0.5 <= price <= 3.0:
                                        all_prices[fuel_name][date].append(price)
                                except (ValueError, TypeError):
                                    continue

            print("ok")

        except requests.RequestException as e:
            print(f"erreur: {e}")
        except ET.ParseError as e:
            print(f"erreur XML: {e}")
        except zipfile.BadZipFile:
            print("erreur: fichier ZIP invalide")

    # Calculer la moyenne journalière pour chaque carburant demandé
    result = {}

    for internal_name, xml_name in config.carburants.items():
        if xml_name is None:
            # Fioul: pas de données, sera généré en démo
            continue

        if xml_name not in all_prices:
            print(f"  ✗ Pas de données pour {internal_name} ({xml_name})")
            continue

        dates = []
        values = []

        for date in sorted(all_prices[xml_name].keys()):
            prices = all_prices[xml_name][date]
            if prices:
                avg_price = sum(prices) / len(prices)
                dates.append(date)
                values.append(round(avg_price, 3))

        if dates:
            result[internal_name] = {"dates": dates, "values": values}
            print(f"  → {internal_name}: {len(values)} points (moyenne/jour)")

    # Générer données démo pour le fioul (non disponible en station)
    if "fioul" not in result:
        print("  ⚠ Fioul domestique non disponible (service livraison)")
        print("  → Génération de données simulées pour le fioul")

    # Si carburants manquants, compléter avec démo
    missing = [k for k, v in config.carburants.items()
               if k not in result and v is None]

    if missing or not result:
        demo_data = _generate_demo_data(config)
        for name in missing:
            if name in demo_data:
                result[name] = demo_data[name]

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


# ============================================================================
# TRAITEMENT DES DONNÉES
# ============================================================================

def clean_and_align_data(baril_data: dict, carburants_data: dict) -> dict:
    """Nettoie et aligne temporellement les données.

    Returns:
        dict avec DataFrame pandas pour chaque série, indexé par date
    """
    # Créer DataFrame pour le baril
    # Ensure same length for dates and values
    min_len = min(len(baril_data["dates"]), len(baril_data["values"]))
    df_baril = pd.DataFrame({
        "date": pd.to_datetime(baril_data["dates"][:min_len]),
        "baril": baril_data["values"][:min_len],
    }).set_index("date").sort_index()

    # Supprimer les doublons et valeurs nulles
    df_baril = df_baril[~df_baril.index.duplicated(keep="first")]
    df_baril = df_baril.dropna()

    # Créer DataFrames pour chaque carburant
    carburant_dfs = {}
    for name, data in carburants_data.items():
        if not data["dates"]:
            continue

        # Ensure same length for dates and values
        min_len = min(len(data["dates"]), len(data["values"]))
        df = pd.DataFrame({
            "date": pd.to_datetime(data["dates"][:min_len]),
            name: data["values"][:min_len],
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


# ============================================================================
# ANALYSE
# ============================================================================

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


# ============================================================================
# VISUALISATION
# ============================================================================

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

    print("[1/5] Récupération données carburants (donnees.roulez-eco.fr)...")
    carburants_data = fetch_fuel_prices(config)

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
