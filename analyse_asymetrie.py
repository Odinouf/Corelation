#!/usr/bin/env python3
"""
Analyse et visualisation de l'asymétrie hausse/baisse.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import analyse_petrole as ap

def main():
    config = ap.Config()
    config.end_date = '2025-12-31'

    print("Chargement des données...")
    baril_data = ap.fetch_fred_data(config)
    carburants_data = ap.fetch_fuel_prices(config)
    aligned = ap.clean_and_align_data(baril_data, carburants_data)

    df = pd.DataFrame({
        'baril': aligned['baril'].iloc[:, 0],
        'diesel': aligned['diesel'].iloc[:, 0],
        'essence': aligned['essence_sp95'].iloc[:, 0],
    })

    delays = [1, 3, 7, 14, 21, 30, 45, 60]
    results = {'diesel': {'up': [], 'down': []}, 'essence': {'up': [], 'down': []}}

    for fuel in ['diesel', 'essence']:
        for delay in delays:
            df['baril_var'] = df['baril'].pct_change()
            df['fuel_var'] = df[fuel].shift(-delay) / df[fuel] - 1

            # Hausses
            mask_up = df['baril_var'] > 0
            x_up = df.loc[mask_up, 'baril_var'].dropna()
            y_up = df.loc[mask_up, 'fuel_var'].dropna()
            common = x_up.index.intersection(y_up.index)
            if len(common) > 10:
                beta_up = (x_up[common] * y_up[common]).sum() / (x_up[common] * x_up[common]).sum()
            else:
                beta_up = np.nan

            # Baisses
            mask_down = df['baril_var'] < 0
            x_down = df.loc[mask_down, 'baril_var'].dropna()
            y_down = df.loc[mask_down, 'fuel_var'].dropna()
            common = x_down.index.intersection(y_down.index)
            if len(common) > 10:
                beta_down = (x_down[common] * y_down[common]).sum() / (x_down[common] * x_down[common]).sum()
            else:
                beta_down = np.nan

            results[fuel]['up'].append(beta_up)
            results[fuel]['down'].append(beta_down)

    # Créer le graphique
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))

    colors = {'diesel': '#1f77b4', 'essence': '#ff7f0e'}

    # Graphique 1: Coefficients β par délai
    ax1 = axes[0]
    for fuel in ['diesel', 'essence']:
        ax1.plot(delays, results[fuel]['up'], color=colors[fuel], linestyle='-',
                 linewidth=2, marker='o', label=f'{fuel} (hausse baril)')
        ax1.plot(delays, results[fuel]['down'], color=colors[fuel], linestyle='--',
                 linewidth=2, marker='s', label=f'{fuel} (baisse baril)')

    ax1.axhline(y=0, color='gray', linestyle='-', alpha=0.3)
    ax1.set_xlabel('Délai (jours)')
    ax1.set_ylabel('Coefficient β de répercussion')
    ax1.set_title('Répercussion des variations du baril\n(β = variation carburant / variation baril)')
    ax1.legend(loc='upper left', fontsize=8)
    ax1.grid(True, alpha=0.3)
    ax1.set_xlim(0, 65)

    # Graphique 2: Asymétrie (β_baisse - β_hausse)
    ax2 = axes[1]
    for fuel in ['diesel', 'essence']:
        asymmetry = [d - u for d, u in zip(results[fuel]['down'], results[fuel]['up'])]
        ax2.plot(delays, asymmetry, color=colors[fuel], linewidth=2, marker='D', label=fuel)
        ax2.fill_between(delays, 0, asymmetry, alpha=0.2, color=colors[fuel],
                        where=[a > 0 for a in asymmetry], interpolate=True)
        ax2.fill_between(delays, 0, asymmetry, alpha=0.1, color='gray',
                        where=[a < 0 for a in asymmetry], interpolate=True)

    ax2.axhline(y=0, color='black', linestyle='-', linewidth=1.5)
    ax2.set_xlabel('Délai (jours)')
    ax2.set_ylabel('Asymétrie (β_baisse - β_hausse)')
    ax2.set_title('Asymétrie de répercussion\n(positif = baisses mieux répercutées)')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    ax2.set_xlim(0, 65)

    # Ajouter annotations
    ax2.annotate('Favorable\nau consommateur', xy=(50, 0.05), fontsize=9, color='green')
    ax2.annotate('Défavorable\n("rockets & feathers")', xy=(50, -0.03), fontsize=9, color='red')

    # Graphique 3: Barres comparatives à différents délais
    ax3 = axes[2]
    x = np.arange(len(delays))
    width = 0.35

    # Calculer asymétrie moyenne diesel+essence
    asym_combined = []
    for i in range(len(delays)):
        a = (results['diesel']['down'][i] - results['diesel']['up'][i] +
             results['essence']['down'][i] - results['essence']['up'][i]) / 2
        asym_combined.append(a)

    colors_bars = ['green' if a > 0 else 'red' for a in asym_combined]
    bars = ax3.bar(x, asym_combined, width, color=colors_bars, alpha=0.7, edgecolor='black')

    ax3.axhline(y=0, color='black', linestyle='-', linewidth=1)
    ax3.set_xlabel('Délai (jours)')
    ax3.set_ylabel('Asymétrie moyenne')
    ax3.set_title('Asymétrie moyenne diesel+essence\n(vert = favorable, rouge = défavorable)')
    ax3.set_xticks(x)
    ax3.set_xticklabels([f'J+{d}' for d in delays])
    ax3.grid(True, alpha=0.3, axis='y')

    # Ajouter valeurs sur les barres
    for bar, val in zip(bars, asym_combined):
        height = bar.get_height()
        ax3.annotate(f'{val:.2f}',
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3 if height > 0 else -12),
                    textcoords="offset points",
                    ha='center', va='bottom' if height > 0 else 'top',
                    fontsize=8)

    plt.suptitle('Analyse de l\'asymétrie hausse/baisse du prix du baril → carburants France',
                 fontsize=12, fontweight='bold', y=1.02)
    plt.tight_layout()

    # Sauvegarder
    os.makedirs('resultats', exist_ok=True)
    output_path = 'resultats/5_asymetrie_hausse_baisse.png'
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()

    print(f"\n→ Graphique sauvegardé: {output_path}")

    # Afficher les résultats numériques
    print("\n" + "=" * 60)
    print("RÉSULTATS DÉTAILLÉS")
    print("=" * 60)
    print(f"{'Délai':>8} | {'Diesel β↑':>10} | {'Diesel β↓':>10} | {'Asym':>8} | " +
          f"{'Essence β↑':>10} | {'Essence β↓':>10} | {'Asym':>8}")
    print("-" * 80)

    for i, d in enumerate(delays):
        d_up = results['diesel']['up'][i]
        d_down = results['diesel']['down'][i]
        e_up = results['essence']['up'][i]
        e_down = results['essence']['down'][i]
        d_asym = d_down - d_up
        e_asym = e_down - e_up
        print(f"J+{d:>5} | {d_up:>+10.3f} | {d_down:>+10.3f} | {d_asym:>+8.3f} | " +
              f"{e_up:>+10.3f} | {e_down:>+10.3f} | {e_asym:>+8.3f}")

    print("\n" + "=" * 60)
    print("CONCLUSION")
    print("=" * 60)
    avg_asym = np.mean([a for a in asym_combined if not np.isnan(a)])
    if avg_asym > 0.02:
        print(f"Asymétrie moyenne: +{avg_asym:.3f}")
        print("→ Les BAISSES du baril sont mieux répercutées que les hausses")
        print("→ Cela est FAVORABLE au consommateur français")
        print("→ L'effet 'rockets and feathers' n'est PAS observé sur ces données")
    else:
        print(f"Asymétrie moyenne: {avg_asym:.3f}")
        print("→ Répercussion relativement symétrique")

if __name__ == "__main__":
    main()
