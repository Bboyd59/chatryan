{pkgs}: {
  deps = [
    pkgs.pulseaudio
    pkgs.alsaLib
    pkgs.alsa-lib
    pkgs.portaudio
    pkgs.openssl
    pkgs.postgresql
  ];
}
