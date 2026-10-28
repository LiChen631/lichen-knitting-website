# -*- coding: utf-8 -*-
"""Set the production site origin and regenerate canonical links + sitemap.xml.

Usage:
    python tools/set_domain.py https://lichen-knitting.pages.dev
    python tools/set_domain.py --clear

Why this exists: the handoff document forbids inventing a domain (no domain has been
purchased or confirmed yet). Until an origin is set, the pages omit <link rel=canonical>,
og:url and sitemap.xml rather than shipping wrong absolute URLs. Run this once the
deployment URL is known.
"""
import io
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG = os.path.join(ROOT, "site.config.json")


def main(argv):
    if len(argv) != 2 or argv[1] in ("-h", "--help"):
        print(__doc__)
        return 2
    arg = argv[1].strip()
    origin = "" if arg in ("--clear", "") else arg.rstrip("/")

    if origin and not re.match(r"^https?://[A-Za-z0-9.\-]+(:\d+)?$", origin):
        print("ERROR: origin must look like https://example.com (got %r)" % origin)
        return 2

    io.open(CONFIG, "w", encoding="utf-8", newline="\n").write(
        json.dumps({"origin": origin}, ensure_ascii=False, indent=2) + "\n"
    )
    if origin:
        print("site.config.json -> origin = %s" % origin)
    else:
        print("site.config.json -> origin cleared")

    sys.path.insert(0, os.path.join(ROOT, "tools"))
    import gen_site

    gen_site.main()
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))