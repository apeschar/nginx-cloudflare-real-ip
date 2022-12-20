{
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = {
    self,
    nixpkgs,
    flake-utils,
  }:
    flake-utils.lib.simpleFlake {
      inherit self nixpkgs;
      name = "nginx-cloudflare-real-ip";
      overlay = final: prev: {
        nginx-cloudflare-real-ip = {
          defaultPackage = prev.python310Packages.buildPythonPackage {
            pname = "nginx-cloudflare-real-ip";
            version = "1.0.0";
            src = ./.;
            format = "pyproject";
            nativeBuildInputs = [prev.python310Packages.setuptools];
          };
        };
      };
    };
}
