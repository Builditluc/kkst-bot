
{ pkgs ? import <nixpkgs> {} }:
let
  python = pkgs.python310;
  python-nextcord = ps: ps.callPackage ./python-packages.nix {};
  python-with-packages = python.withPackages (ps: with ps; [
    pip
    (python-nextcord ps)
  ]);
in
pkgs.mkShell {
  buildInputs = [
    python-with-packages
  ];
  shellHook = "PYTHONPATH=${python-with-packages}/${python-with-packages.sitePackages}";
}

