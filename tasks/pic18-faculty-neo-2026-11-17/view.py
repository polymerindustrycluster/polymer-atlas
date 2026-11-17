#!/usr/bin/env python3
"""view.py HASHPREFIX [links] : print visible text (or links) of a stored witness."""
import os, re, html, sys
P = "/Users/johnswanson/.bb/thread-storage/thr_9i2c6byhcz/2026-11-06-atlas/persist/pic18-faculty-neo-2026-11-17/"
def raw(prefix):
    f = [x for x in os.listdir(P) if x.startswith(prefix)][0]
    return open(P + f, errors="ignore").read()
def text(t):
    t = re.sub(r"<script.*?</script>|<style.*?</style>", "", t, flags=re.S)
    t = re.sub(r"<[^>]+>", "\n", t); t = html.unescape(t)
    return [l.strip() for l in t.split("\n") if l.strip()]
if __name__ == "__main__":
    t = raw(sys.argv[1])
    if len(sys.argv) > 2 and sys.argv[2] == "links":
        pat = sys.argv[3] if len(sys.argv) > 3 else ""
        for m in re.finditer(r'<a [^>]*href="([^"]+)"[^>]*>(.*?)</a>', t, flags=re.S):
            lab = re.sub(r"<[^>]+>", " ", m.group(2)); lab = " ".join(html.unescape(lab).split())
            if pat in m.group(1) or pat in lab: print(m.group(1), "|", lab[:60])
    else:
        print("\n".join(text(t)))
