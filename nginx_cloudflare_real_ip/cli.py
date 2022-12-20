#!/usr/bin/env python3

import sys
from argparse import ArgumentParser
from ipaddress import ip_network
from pathlib import Path
from secrets import token_urlsafe
from urllib.request import Request, urlopen

parser = ArgumentParser()
parser.add_argument("--out-file", "-o")

IP_LIST_URLS = (
    "https://www.cloudflare.com/ips-v4",
    "https://www.cloudflare.com/ips-v6",
)


def main():
    args = parser.parse_args()
    ips = get_ips()
    config = generate_config(ips)

    if args.out_file is not None:
        atomic_write(args.out_file, config)
    else:
        sys.stdout.write(config)

    return 0


def get_ips():
    for url in IP_LIST_URLS:
        yield from get_ips_from_url(url)


def get_ips_from_url(url):
    log("GET %s" % url)
    request = Request(url)
    request.add_header("User-Agent", "")
    with urlopen(request) as f:
        for line in f:
            line = line.decode("utf-8").strip()
            try:
                addr = ip_network(line)
            except ValueError:
                log("Got invalid IP: %r" % line)
            else:
                yield addr


def generate_config(ips):
    return "".join(line + "\n" for line in generate_config_lines(ips))


def generate_config_lines(ips):
    ips = sorted(ips, key=lambda ip: (ip.version, ip))
    for ip in ips:
        yield f"set_real_ip_from {ip};"
    yield "real_ip_header CF-Connecting-IP;"


def log(message):
    print(message, file=sys.stderr)


def atomic_write(dest, contents):
    dest = Path(dest)
    tmp = dest.with_name(".%s.%s" % (dest.name, token_urlsafe()))
    try:
        tmp.write_text(contents, encoding="utf-8")
        tmp.rename(dest)
    finally:
        tmp.unlink(missing_ok=True)
