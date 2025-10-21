{ pkgs }: {
  deps = [
    pkgs.python3
    pkgs.python3Packages.pip
    pkgs.python3Packages.requests
    pkgs.python3Packages.feedparser
    pkgs.python3Packages.python-dotenv
    pkgs.nodejs-18_x
    pkgs.curl
    pkgs.wget
  ];
}