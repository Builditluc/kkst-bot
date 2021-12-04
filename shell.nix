let pkgs = import <nixpkgs> { };
in
let
  packageOverrides = pkgs.callPackage ./python-packages.nix { };
  python = pkgs.python39.override { inherit packageOverrides; };
  pythonWithPackages = python.withPackages (ps: [ ps.nextcord ]);
in
pkgs.mkShell {
  nativeBuildInputs = [ pythonWithPackages ];
}
