"""Parse a uakron dotCMS people listing page -> [(name, title, dept, profile_u)]. Drops phone/email at parse time."""
import re, html
def parse(raw):
    h = raw.decode("utf-8", "replace")
    h = re.sub(r"<script.*?</script>|<style.*?</style>", "", h, flags=re.S)
    i = h.find("Our Faculty")
    t = html.unescape(re.sub(r"<[^>]+>", "\n", h[i:]))
    lines = [l.strip() for l in t.split("\n") if l.strip()]
    out = []
    for k, l in enumerate(lines):
        if l == "Title:" and k >= 1:
            name = lines[k - 1]
            title = lines[k + 1]
            dept = lines[lines.index("Dept/Program:", k) + 1] if "Dept/Program:" in lines[k:k + 12] else ""
            out.append([name, title, dept])
    us = re.findall(r"profile\.dot\?u=([A-Za-z0-9_.-]+)", h[i:])
    seen = []
    [seen.append(u) for u in us if u not in seen]
    return out, seen
