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
