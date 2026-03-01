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

- **Baril Brent**: [FRED](https://fred.stlouisfed.org/series/DCOILBRENTEU) - API ouverte sans clé requise
- **Carburants France**: [donnees.roulez-eco.fr](https://donnees.roulez-eco.fr) - Ministère de la Transition Écologique, données ouvertes sans clé API

Aucune clé API n'est nécessaire.

## Carburants analysés

| Carburant | Source | Notes |
|-----------|--------|-------|
| Diesel (Gazole) | donnees.roulez-eco.fr | Données réelles |
| Essence (E10/SP95) | donnees.roulez-eco.fr | Données réelles |
| Fioul domestique | Simulé | Non disponible en station (livraison uniquement) |

## Résultats typiques

- **Corrélation directe**: 0.78-0.83 (forte)
- **Corrélation avec délai**: 0.82-0.89 (très forte)
- **Délai optimal**: 23-38 jours selon le carburant

Le délai représente le temps nécessaire pour qu'une variation du prix du baril se répercute pleinement sur les prix à la pompe.
