{
  description = "Field-updated NixOS appliance";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-25.05";
    sbomnix.url = "github:tiiuae/sbomnix";
    sbomnix.inputs.nixpkgs.follows = "nixpkgs";
  };

  outputs = { self, nixpkgs, sbomnix }: {
    nixosConfigurations.appliance = nixpkgs.lib.nixosSystem {
      system = "x86_64-linux";
      modules = [ ./configuration.nix ];
    };
    packages.x86_64-linux.sbomnix = sbomnix.packages.x86_64-linux.default;
  };
}
