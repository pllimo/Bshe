#!/usr/bin/env python3
"""Replace every assets/xxx reference in index.html with an inline base64 data URI."""
import base64, mimetypes, pathlib, re, sys

SRC = pathlib.Path(__file__).parent / "index.html"
OUT = pathlib.Path(__file__).parent / "index-portable.html"

html = SRC.read_text(encoding="utf-8")
refs = sorted(set(re.findall(r"assets/[^'\")\s]+", html)))
print(f"Found {len(refs)} unique asset references")

data_uris = {}
total_in = 0
for ref in refs:
    p = SRC.parent / ref
    if not p.exists():
        print(f"  MISSING: {ref}", file=sys.stderr); continue
    mime, _ = mimetypes.guess_type(p.name)
    if not mime: mime = "application/octet-stream"
    blob = p.read_bytes()
    total_in += len(blob)
    b64 = base64.b64encode(blob).decode("ascii")
    data_uris[ref] = f"data:{mime};base64,{b64}"
    print(f"  {ref:38} {len(blob)/1024:8.1f} KB → {len(b64)/1024:8.1f} KB ({mime})")

for ref, uri in data_uris.items():
    html = html.replace(ref, uri)

OUT.write_text(html, encoding="utf-8")
size_out = OUT.stat().st_size
print(f"\nWrote {OUT.name}  ({size_out/1024/1024:.1f} MB,  source images {total_in/1024/1024:.1f} MB)")
