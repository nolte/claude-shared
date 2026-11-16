{ config, pkgs, lib, ... }:
{
  system.stateVersion = "25.05";
  system.image.id = "appliance";
  system.image.version = "3.0.0";

  boot.loader.systemd-boot.enable = true;
  boot.loader.systemd-boot.bootCounting.enable = true;
  boot.loader.systemd-boot.bootCounting.tries = 3;
  boot.loader.systemd-boot.configurationLimit = 3;

  nix.settings.require-sigs = true;
  nix.settings.trusted-public-keys = [ "cache.nixos.org-1:6NCHdD59X431o0gWypbMrAURkbJ16ZPMQFGspcDShjY=" ];

  systemd.services.appliance-health = {
    description = "Appliance health definition";
    before = [ "boot-complete.target" ];
    requiredBy = [ "boot-complete.target" ];
    serviceConfig = {
      Type = "oneshot";
      RemainAfterExit = true;
      ImportCredential = "image.health.fail-version";
      ExecStart = "${pkgs.bash}/bin/sh ${./appliance-health}";
      FailureAction = "reboot";
    };
  };

  environment.etc."appliance-build-stamp".text = toString builtins.currentTime;
}
