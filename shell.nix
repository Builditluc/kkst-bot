
{ pkgs ? import <nixpkgs> {} }:
let
  python = pkgs.python39;
  python-with-packages = python.withPackages (p: with p; [
    pip
    discordpy
  ]);
in
pkgs.mkShell {
  buildInputs = [
    python-with-packages
  ];
  shellHook = "PYTHONPATH=${python-with-packages}/${python-with-packages.sitePackages}";
}

