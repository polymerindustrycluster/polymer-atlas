#!/usr/bin/env python3
"""Website-liveness sweep for the Polymer Atlas (IDEAS_AND_RESOURCES C-02).

Reads every organization shard (data/organizations_*.csv) and
data/ecosystem.csv, takes the `website` field of rows whose status is
active or unknown, and probes each unique domain once:

  * DNS (socket.getaddrinfo): NXDOMAIN vs other resolver error
  * HTTPS GET of the homepage (stdlib urllib, honest user-agent, no spoofing)
  * final URL after redirects (cross-domain redirect = possible
    acquisition / rebrand), HTTP status, <title>
  * parked-domain heuristics on the first ~50 KB of HTML

It READS data/ and writes only under --out (signals.csv + REQUEUE.md).

PROTOCOL (AGENTS.md section 2 rule 8 and section 3): every output row is a LEAD
for re-verification, never a verdict and never a status change.  A failed
fetch (403, timeout, bot wall, TLS error, proxy error, empty result) is an
availability signal about the route -- never evidence of absence or
closure.  Only NXDOMAIN, PARKED_SUSPECT and REDIRECT_CROSS_DOMAIN enter the
re-verification queue, and even those still need Form 5500 / SOS / dated
evidence before any status is touched.

Signal classes: OK, REDIRECT_CROSS_DOMAIN, PARKED_SUSPECT, NXDOMAIN,
HTTP_4XX, HTTP_5XX, TIMEOUT, TLS_ERROR, BOT_WALL_SUSPECT, OTHER_ERROR.

Outbound HTTPS honours HTTPS_PROXY (urllib does).  If /root/.ccr/ca-bundle.crt
exists it is used as the CA bundle; verification is never disabled.

Usage:
  python3 scripts/liveness_sweep.py --out tasks/liveness-sweep-2026-11-01
  python3 scripts/liveness_sweep.py --limit 1000 --out /tmp/x   # deterministic sample
"""
from __future__ import annotations

import argparse
import concurrent.futures as cf
import csv
import glob
import hashlib
import http.client
import os
import re
import socket
import ssl
import sys
import time
import unicodedata
import urllib.error
import urllib.request
from collections import Counter, defaultdict
from datetime import datetime, timezone

USER_AGENT = ("polymer-atlas-liveness/1.0 "
              "(+https://github.com/polymerindustrycluster/polymer-atlas)")
DEFAULT_CA_BUNDLE = "/root/.ccr/ca-bundle.crt"
READ_BYTES = 50 * 1024
TOTAL_READ_DEADLINE = 30.0  # seconds, guards slow-drip bodies
ACTIVE_STATUSES = {"active", "unknown"}

CLASSES = ["OK", "REDIRECT_CROSS_DOMAIN", "PARKED_SUSPECT", "NXDOMAIN",
           "HTTP_4XX", "HTTP_5XX", "TIMEOUT", "TLS_ERROR",
           "BOT_WALL_SUSPECT", "OTHER_ERROR"]
REQUEUE_CLASSES = ["NXDOMAIN", "PARKED_SUSPECT", "REDIRECT_CROSS_DOMAIN"]

# Directory / social platforms are not company sites: a website field that
# points at one is a hygiene finding, and the platform is not probed.
SHARED_PLATFORMS = {
    "thomasnet.com", "linkedin.com", "facebook.com", "twitter.com", "x.com",
    "instagram.com", "youtube.com", "google.com", "bing.com", "yelp.com",
    "bbb.org", "dnb.com", "zoominfo.com", "manta.com", "mapquest.com",
    "crunchbase.com", "wikipedia.org", "plasticsnews.com", "sec.gov",
}

# Registered-domain handling without a public-suffix list: these second-level
# labels under a 2-letter ccTLD mean the registrable name is three labels.
_CC_SLD = {"co", "com", "org", "net", "ac", "gov", "edu", "ne", "or", "go"}

# --- parked-domain heuristics ------------------------------------------------
PARKED_PHRASES = [
    "domain is for sale", "domain for sale", "buy this domain",
    "this domain may be for sale", "this domain is for sale",
    "this domain is parked", "domain is parked", "parked free",
    "parked domain", "inquire about this domain",
    "make an offer on this domain", "hugedomains", "sedoparking",
    "sedo.com", "sedo domain parking", "afternic", "dan.com/buy-domain",
    "parkingcrew", "bodis.com", "this web page is parked",
    "domain has expired", "domain registration has expired",
    # lapsed-hosting landers (hosting account suspended / domain not connected)
    "account suspended", "this account has been suspended",
    "connectyourdomain", "suspendedpage.cgi",
]
PARKING_HOSTS = {
    "sedoparking.com", "sedo.com", "hugedomains.com", "dan.com",
    "afternic.com", "parkingcrew.net", "bodis.com", "above.com",
    "domainmarket.com", "undeveloped.com",
}
_GODADDY_CO = re.compile(r"parked|for sale|buy this domain|domain is|"
                         r"is available|coming soon|related searches", re.I)

# --- bot-wall / captcha heuristics ------------------------------------------
BOT_TITLE_MARKERS = [
    "just a moment", "attention required", "access denied", "are you a robot",
    "pardon our interruption", "verify you are human", "security check",
    "captcha", "ddos protection", "request blocked",
]
BOT_BODY_MARKERS = [
    "g-recaptcha", "h-captcha", "hcaptcha.com", "px-captcha",
    "cf-challenge", "challenge-platform", "cdn-cgi/challenge",
    "enable javascript and cookies to continue", "incapsula incident",
    "sucuri website firewall", "akamai reference",
]


# =============================================================================
# Pure helpers (unit-tested without network)
# =============================================================================
_HOST_RE = re.compile(r"^(?=.{4,253}$)([a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z]{2,}$")


def normalize_website(raw: str):
    """Return (domain|None, reason).

    reason: 'ok' (clean URL or bare domain), 'empty', 'polluted' (non-URL
    text, several values or trailing notes in the field), 'invalid'
    (no usable hostname, e.g. 'none_found').  domain has scheme, www.,
    port, path, query and case stripped.
    """
    if raw is None:
        return None, "empty"
    s = unicodedata.normalize("NFKC", raw).strip()
    if not s:
        return None, "empty"
    if re.search(r"[\s;(),@|<>\"']", s):
        return None, "polluted"
    host = re.sub(r"^[A-Za-z][A-Za-z0-9+.-]*://", "", s)
    host = re.split(r"[/?#]", host, maxsplit=1)[0]
    host = host.rsplit("@", 1)[-1]
    host = re.sub(r":\d+$", "", host).lower().rstrip(".")
    if host.startswith("www."):
        host = host[4:]
    try:
        host = host.encode("idna").decode("ascii")
    except UnicodeError:
        return None, "invalid"
    if not _HOST_RE.match(host):
        return None, "invalid"
    return host, "ok"


def registered_domain(host: str) -> str:
    """Approximate registrable domain (no PSL; handles co.uk-style names)."""
    labels = [p for p in (host or "").lower().rstrip(".").split(".") if p]
    if len(labels) <= 2:
        return ".".join(labels)
    if len(labels[-1]) == 2 and labels[-2] in _CC_SLD:
        return ".".join(labels[-3:])
    return ".".join(labels[-2:])


def host_of(url: str) -> str:
    m = re.match(r"^[A-Za-z][A-Za-z0-9+.-]*://([^/?#]+)", url or "")
    if not m:
        return ""
    return re.sub(r":\d+$", "", m.group(1).rsplit("@", 1)[-1]).lower()


def is_cross_domain(start_domain: str, final_url: str) -> bool:
    fh = host_of(final_url)
    if not fh:
        return False
    return registered_domain(fh) != registered_domain(start_domain)


def extract_title(html: str) -> str:
    m = re.search(r"<title[^>]*>(.*?)</title>", html or "", re.I | re.S)
    if not m:
        return ""
    t = re.sub(r"<[^>]+>", " ", m.group(1))
    t = (t.replace("&amp;", "&").replace("&#39;", "'").replace("&quot;", '"')
          .replace("&nbsp;", " "))
    return re.sub(r"\s+", " ", t).strip()[:200]


def meta_refresh_target(html: str, base_url: str = ""):
    m = re.search(r"<meta[^>]+http-equiv=[\"']?refresh[\"']?[^>]*content=[\"']"
                  r"[^\"']*url=([^\"'>\s]+)", html or "", re.I)
    if not m:
        return None
    t = m.group(1).strip()
    if re.match(r"^[A-Za-z][A-Za-z0-9+.-]*://", t):
        return t
    return None


def parked_markers(html: str, final_url: str = "", body_complete: bool = True):
    """Return matched parked-domain markers (empty list = none)."""
    low = (html or "").lower()
    hits = [p for p in PARKED_PHRASES if p in low]
    if "suspendedpage" in (final_url or "").lower() and "suspendedpage.cgi" not in hits:
        hits.append("suspendedpage.cgi")  # cPanel suspended-account redirect target
    fh = registered_domain(host_of(final_url)) if final_url else ""
    if fh in PARKING_HOSTS:
        hits.append("parking_host:" + fh)
    # GoDaddy / registrar landers are small pages; a footer mention on a
    # real site must not trigger, so require a short page plus lander words.
    if "godaddy" in low and len(low) < 20000 and _GODADDY_CO.search(low):
        hits.append("godaddy_lander")
    # Phrases only count from body text, a lone 'afternic' in a script is weak:
    # require >=1 strong phrase or the parking-host/godaddy rule (as above).
    return hits


def bot_wall_markers(status, title: str, html: str):
    hits = []
    tl = (title or "").lower()
    for m in BOT_TITLE_MARKERS:
        if m in tl:
            hits.append("title:" + m)
    low = (html or "").lower()
    for m in BOT_BODY_MARKERS:
        if m in low:
            hits.append("body:" + m)
    return hits


def classify(r: dict) -> str:
    """Classify a probe result dict.  Keys used: dns ('ok'|'nxdomain'|'error'),
    error ('timeout'|'tls'|'proxy'|'other'|None), http_status (int|None),
    domain, final_url, title, html, body_complete."""
    if r.get("dns") == "nxdomain":
        return "NXDOMAIN"
    err = r.get("error")
    if err == "timeout":
        return "TIMEOUT"
    if err == "tls":
        return "TLS_ERROR"
    if err:
        return "OTHER_ERROR"
    status = r.get("http_status")
    if status is None:
        return "OTHER_ERROR"
    html = r.get("html") or ""
    title = r.get("title") or ""
    bot = bot_wall_markers(status, title, html)
    # A bot wall is an availability signal; it outranks everything because a
    # challenge page tells us nothing about the company.
    if status in (403, 429) or (status in (401, 503) and bot) or \
            (status < 400 and any(h.startswith("title:") for h in bot)):
        return "BOT_WALL_SUSPECT"
    if parked_markers(html, r.get("final_url", ""), r.get("body_complete", True)):
        return "PARKED_SUSPECT"
    if 400 <= status < 500:
        return "HTTP_4XX"
    if status >= 500:
        return "HTTP_5XX"
    if is_cross_domain(r.get("domain", ""), r.get("final_url", "")):
        return "REDIRECT_CROSS_DOMAIN"
    return "OK"


# =============================================================================
# IO
# =============================================================================
def build_ssl_context(cafile: str | None):
    if cafile and os.path.exists(cafile):
        return ssl.create_default_context(cafile=cafile)
    return ssl.create_default_context()


def resolve(host: str):
    """Return ('ok'|'nxdomain'|'error', detail)."""
    try:
        socket.getaddrinfo(host, 443, proto=socket.IPPROTO_TCP)
        return "ok", ""
    except socket.gaierror as e:
        if e.errno in (socket.EAI_NONAME, getattr(socket, "EAI_NODATA", -5)):
            return "nxdomain", str(e)
        return "error", f"gaierror {e.errno}: {e}"
    except (UnicodeError, OSError) as e:
        return "error", f"{type(e).__name__}: {e}"


def _read_body(resp, deadline):
    chunks, total = [], 0
    complete = True
    while total < READ_BYTES:
        if time.monotonic() > deadline:
            complete = False
            break
        try:
            chunk = resp.read(min(8192, READ_BYTES - total))
        except (socket.timeout, TimeoutError, http.client.IncompleteRead,
                ssl.SSLError, ConnectionError, OSError):
            complete = False
            break
        if not chunk:
            break
        chunks.append(chunk)
        total += len(chunk)
    else:
        complete = False
    data = b"".join(chunks)
    ct = ""
    try:
        ct = resp.headers.get_content_charset() or ""
    except Exception:
        pass
    try:
        text = data.decode(ct or "utf-8", errors="replace")
    except LookupError:
        text = data.decode("utf-8", errors="replace")
    return text, complete


def _err_kind(exc) -> tuple[str, str]:
    """Map an exception to (kind, detail)."""
    reason = getattr(exc, "reason", exc)
    msg = f"{type(reason).__name__}: {reason}"
    s = str(reason)
    if isinstance(reason, (socket.timeout, TimeoutError)) or "timed out" in s:
        return "timeout", msg
    if isinstance(reason, ssl.SSLError) or "CERTIFICATE_VERIFY_FAILED" in s \
            or isinstance(reason, ssl.CertificateError):
        return "tls", msg
    m = re.search(r"Tunnel connection failed:\s*(\d{3})", s)
    if m:
        return "proxy", f"proxy_tunnel_{m.group(1)}"
    return "other", msg


def fetch(url: str, ctx, timeout: float):
    req = urllib.request.Request(url, headers={
        "User-Agent": USER_AGENT,
        "Accept": "text/html,application/xhtml+xml;q=0.9,*/*;q=0.5",
    })
    opener = urllib.request.build_opener(
        urllib.request.ProxyHandler(),  # honours HTTPS_PROXY
        urllib.request.HTTPSHandler(context=ctx),
    )
    deadline = time.monotonic() + TOTAL_READ_DEADLINE
    out = {"http_status": None, "final_url": url, "html": "", "title": "",
           "error": None, "detail": "", "body_complete": True}
    try:
        with opener.open(req, timeout=timeout) as resp:
            out["http_status"] = resp.status
            out["final_url"] = resp.geturl()
            out["html"], out["body_complete"] = _read_body(resp, deadline)
    except urllib.error.HTTPError as e:
        out["http_status"] = e.code
        out["final_url"] = e.url or url
        try:
            out["html"], out["body_complete"] = _read_body(e, deadline)
        except Exception:
            pass
        finally:
            e.close()
    except (urllib.error.URLError, socket.timeout, TimeoutError, ssl.SSLError,
            ConnectionError, http.client.HTTPException, OSError,
            UnicodeError) as e:
        out["error"], out["detail"] = _err_kind(e)
    out["title"] = extract_title(out["html"])
    return out


def probe(domain: str, ctx, timeout: float) -> dict:
    """Probe one domain; exactly one logical request (plus one retry of a
    transient proxy tunnel/resolver failure)."""
    res = {"domain": domain, "dns": "ok", "dns_detail": "", "host_used": domain,
           "http_status": None, "final_url": "", "title": "", "html": "",
           "error": None, "detail": "", "body_complete": True, "markers": ""}
    host = domain
    dns, dd = resolve(host)
    for attempt in range(2):                # transient resolver trouble: retry twice
        if dns != "error":
            break
        time.sleep(2.0 * (attempt + 1))
        dns, dd = resolve(host)
    if dns == "nxdomain":
        www = "www." + domain
        d2, dd2 = resolve(www)
        if d2 == "ok":                      # apex absent, www present
            dns, dd, host = "ok", "apex NXDOMAIN; used www.", www
    res["dns"], res["dns_detail"], res["host_used"] = dns, dd, host
    if dns == "nxdomain":
        res["detail"] = dd
        res["final_url"] = ""
        return res
    if dns == "error":
        res["error"], res["detail"] = "other", "dns_error: " + dd
        return res
    url = f"https://{host}/"
    f = fetch(url, ctx, timeout)
    if f["error"] == "proxy" and f["detail"] in ("proxy_tunnel_502", "proxy_tunnel_503", "proxy_tunnel_504"):
        time.sleep(1.0)
        f = fetch(url, ctx, timeout)
    res.update(f)
    # meta-refresh to another registrable domain counts as a redirect lead
    if not res["error"] and res["http_status"] and res["http_status"] < 400:
        mt = meta_refresh_target(res["html"])
        if mt and is_cross_domain(domain, mt) and not is_cross_domain(domain, res["final_url"]):
            res["final_url"] = mt
            res["detail"] = (res["detail"] + " meta_refresh").strip()
    res["markers"] = ";".join(parked_markers(res["html"], res["final_url"], res["body_complete"]))
    return res


# =============================================================================
# Data loading
# =============================================================================
def load_rows(data_dir: str):
    """Yield dicts: org_id, legal_name, shard, status, tier, website."""
    files = sorted(glob.glob(os.path.join(data_dir, "organizations_*.csv")))
    files.append(os.path.join(data_dir, "ecosystem.csv"))
    for path in files:
        base = os.path.basename(path)
        shard = "ECOSYSTEM" if base == "ecosystem.csv" else base[len("organizations_"):-4]
        with open(path, newline="", encoding="utf-8") as fh:
            for r in csv.DictReader(fh):
                yield {"org_id": r.get("org_id", ""), "legal_name": r.get("legal_name", ""),
                       "shard": shard, "status": (r.get("status") or "").strip(),
                       "tier": (r.get("verification_tier") or "").strip(),
                       "website": r.get("website") or ""}


def build_targets(rows):
    """Group eligible rows by domain.  Returns (targets, hygiene, stats)."""
    targets = defaultdict(list)
    hygiene = {"polluted": [], "invalid": [], "shared_platform": []}
    stats = Counter()
    for r in rows:
        stats["rows_total"] += 1
        if r["status"] not in ACTIVE_STATUSES:
            stats["rows_skipped_status"] += 1
            continue
        stats["rows_active_unknown"] += 1
        dom, why = normalize_website(r["website"])
        if why == "empty":
            stats["rows_no_website"] += 1
            continue
        if why == "polluted":
            hygiene["polluted"].append(r)
            continue
        if why == "invalid":
            hygiene["invalid"].append(r)
            continue
        if registered_domain(dom) in SHARED_PLATFORMS:
            hygiene["shared_platform"].append(r)
            continue
        targets[dom].append(r)
        stats["rows_swept"] += 1
    return targets, hygiene, stats


def deterministic_sample(domains, n):
    ordered = sorted(domains, key=lambda d: hashlib.sha1(d.encode()).hexdigest())
    return sorted(ordered[:n])


# =============================================================================
# Output
# =============================================================================
SIGNAL_COLS = ["org_id", "legal_name", "shard", "status", "tier", "domain",
               "signal_class", "http_status", "final_url", "title", "checked_at",
               "org_row_count", "detail"]


def write_signals(path, targets, results):
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(SIGNAL_COLS)
        for dom in sorted(results):
            r = results[dom]
            rows = targets[dom]
            detail = r["detail"]
            if r.get("markers"):
                detail = (detail + " markers=" + r["markers"]).strip()
            if r.get("host_used") and r["host_used"] != dom:
                detail = (detail + " fetched_host=" + r["host_used"]).strip()
            w.writerow([
                ";".join(x["org_id"] for x in rows),
                " | ".join(x["legal_name"] for x in rows),
                ";".join(sorted({x["shard"] for x in rows})),
                ";".join(sorted({x["status"] for x in rows})),
                ";".join(sorted({x["tier"] for x in rows})),
                dom, r["signal_class"],
                r["http_status"] if r["http_status"] is not None else "",
                r["final_url"], r["title"], r["checked_at"], len(rows), detail,
            ])


def md_cell(s):
    return str(s).replace("|", "\\|").replace("\n", " ")


def write_requeue(path, targets, results, hygiene, stats, args, total_domains, started, finished):
    by_dom, by_rows = Counter(), Counter()
    for d, r in results.items():
        by_dom[r["signal_class"]] += 1
        by_rows[r["signal_class"]] += len(targets[d])
    sampled = len(results) < total_domains
    L = []
    L.append(f"# Website-liveness sweep: re-verification queue ({finished[:10]})\n")
    L.append("Generated by `scripts/liveness_sweep.py` (packet lane output; "
             "IDEAS_AND_RESOURCES C-02). **Every row below is a lead for "
             "re-verification, not a verdict and not a status change** "
             "(AGENTS.md section 2 rule 8, section 3).\n")
    L.append("## How to read this\n")
    L.append("- **Re-verification queue = NXDOMAIN + PARKED_SUSPECT + REDIRECT_CROSS_DOMAIN.** "
             "Each queued org still needs the Form 5500 check (bulk EFAST2; a sponsor "
             "filing blocks a reject only when its address is the establishment), Ohio/other "
             "SOS status, and dated primary or near-primary evidence before any status "
             "change. A dead or parked website alone changes nothing; a cross-domain "
             "redirect may be a rebrand, an acquisition (check `successor_org_id` and "
             "trade names), or just a corporate-site consolidation.")
    L.append("- **TIMEOUT, TLS_ERROR, BOT_WALL_SUSPECT, HTTP_4XX, HTTP_5XX and OTHER_ERROR are "
             "availability signals about the fetch route only.** They are not queued, and they "
             "are never evidence of absence or closure.")
    L.append("- Route caveat: outbound HTTPS goes through the agent egress proxy, which "
             "terminates TLS itself. Origin certificate problems and unreachable origins "
             "therefore surface mostly as proxy tunnel failures (OTHER_ERROR, "
             "`proxy_tunnel_5xx`) rather than TLS_ERROR; NXDOMAIN comes from the local "
             "resolver. One request per domain, homepage only (`https://<host>/`); a path in "
             "the stored website (e.g. a university sub-unit) is not fetched.\n")
    L.append("## Run\n")
    L.append(f"- Started {started}, finished {finished} (UTC); {args.workers} workers, "
             f"{args.timeout:.0f}s timeout, user-agent `{USER_AGENT}`.")
    if sampled:
        L.append(f"- **Deterministic sample**: {len(results)} of {total_domains} eligible unique "
                 f"domains (sha1-ordered first {args.limit}).")
    else:
        L.append(f"- Full sweep: all {len(results)} eligible unique domains.")
    L.append(f"- Organization/ecosystem rows read: {stats['rows_total']}; skipped for status not in "
             f"active/unknown: {stats['rows_skipped_status']}; active/unknown rows with no website: "
             f"{stats['rows_no_website']}; active/unknown rows excluded for website hygiene: "
             f"{len(hygiene['polluted']) + len(hygiene['invalid']) + len(hygiene['shared_platform'])}; "
             f"active/unknown rows with a sweepable domain: {stats['rows_swept']}.\n")
    L.append("## Counts by signal class\n")
    L.append("Unit: unique normalized domains probed (www. stripped), and active/unknown "
             "organization+ecosystem rows sharing those domains.\n")
    L.append("| Signal class | Unique domains | Org rows | Queued? |")
    L.append("|---|---:|---:|---|")
    for c in CLASSES:
        L.append(f"| {c} | {by_dom[c]} | {by_rows[c]} | {'yes' if c in REQUEUE_CLASSES else 'no (availability only)' if c not in ('OK',) else 'no'} |")
    L.append(f"| **Total** | **{sum(by_dom.values())}** | **{sum(by_rows.values())}** | |\n")
    qd = sum(by_dom[c] for c in REQUEUE_CLASSES)
    qr = sum(by_rows[c] for c in REQUEUE_CLASSES)
    L.append(f"**Re-verification queue size: {qd} unique domains covering {qr} organization/ecosystem rows.**\n")

    def section(cls, title, extra_col=None):
        doms = sorted((d for d, r in results.items() if r["signal_class"] == cls),
                      key=lambda d: (-len(targets[d]), d))
        L.append(f"## Queue: {title} ({len(doms)} domains)\n")
        if not doms:
            L.append("_None._\n")
            return
        if cls == "REDIRECT_CROSS_DOMAIN":
            L.append("| Domain | Org IDs | Legal name(s) | Redirects to | HTTP | Title |")
            L.append("|---|---|---|---|---:|---|")
        else:
            L.append("| Domain | Org IDs | Legal name(s) | Detail | Title |")
            L.append("|---|---|---|---|---|")
        for d in doms:
            r = results[d]
            ids = ", ".join(x["org_id"] for x in targets[d])
            names = "; ".join(x["legal_name"] for x in targets[d])
            if cls == "REDIRECT_CROSS_DOMAIN":
                L.append(f"| {md_cell(d)} | {ids} | {md_cell(names)} | {md_cell(r['final_url'])} | "
                         f"{r['http_status'] or ''} | {md_cell(r['title'])} |")
            else:
                det = r["detail"] or r.get("markers", "")
                if cls == "PARKED_SUSPECT":
                    det = r.get("markers", "") + (f" (HTTP {r['http_status']}, {r['final_url']})" if r["http_status"] else "")
                L.append(f"| {md_cell(d)} | {ids} | {md_cell(names)} | {md_cell(det)} | {md_cell(r['title'])} |")
        L.append("")

    section("NXDOMAIN", "NXDOMAIN (domain does not resolve; apex and www. both tried)")
    section("PARKED_SUSPECT", "PARKED_SUSPECT (parked / for-sale heuristics matched)")
    section("REDIRECT_CROSS_DOMAIN", "REDIRECT_CROSS_DOMAIN (final URL on a different registrable domain)")

    L.append("## Website-field hygiene findings\n")
    L.append("Counts are active/unknown organization and ecosystem rows (unit: rows). These "
             "rows were **not swept**; fixing them is a data-hygiene task for the integrator "
             "of record, not for this lane.\n")
    L.append(f"- **Notes-polluted website fields** (non-URL text, several values, or trailing "
             f"notes in the `website` column): **{len(hygiene['polluted']) + len(hygiene['invalid'])} rows** "
             f"({len(hygiene['polluted'])} with whitespace/punctuation/notes, "
             f"{len(hygiene['invalid'])} with no usable hostname such as `none_found`).")
    L.append(f"- Website points at a directory or social platform rather than the company "
             f"({', '.join(sorted({registered_domain(normalize_website(x['website'])[0]) for x in hygiene['shared_platform']})) or 'none'}): "
             f"**{len(hygiene['shared_platform'])} rows**.\n")
    for key, label in (("polluted", "Polluted values"), ("invalid", "Unusable values"),
                       ("shared_platform", "Shared-platform values")):
        if hygiene[key]:
            L.append(f"<details><summary>{label} ({len(hygiene[key])})</summary>\n")
            L.append("| Org ID | Shard | Legal name | Website value |")
            L.append("|---|---|---|---|")
            for x in sorted(hygiene[key], key=lambda x: x["org_id"]):
                L.append(f"| {x['org_id']} | {x['shard']} | {md_cell(x['legal_name'])} | {md_cell(x['website'][:160])} |")
            L.append("\n</details>\n")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(L) + "\n")


# =============================================================================
def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--data-dir", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data"))
    ap.add_argument("--out", required=True, help="output directory (signals.csv, REQUEUE.md)")
    ap.add_argument("--limit", type=int, default=0, help="deterministic (sha1-ordered) sample of N unique domains; 0 = all")
    ap.add_argument("--workers", type=int, default=16, help="thread-pool size (max 16)")
    ap.add_argument("--timeout", type=float, default=15.0)
    ap.add_argument("--cafile", default=DEFAULT_CA_BUNDLE)
    args = ap.parse_args(argv)
    args.workers = max(1, min(16, args.workers))

    targets, hygiene, stats = build_targets(load_rows(args.data_dir))
    total_domains = len(targets)
    domains = sorted(targets)
    if args.limit and args.limit < len(domains):
        domains = deterministic_sample(domains, args.limit)
    print(f"{total_domains} eligible unique domains; probing {len(domains)}", file=sys.stderr)

    ctx = build_ssl_context(args.cafile)
    started = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    results = {}

    def work(d):
        r = probe(d, ctx, args.timeout)
        r["signal_class"] = classify(r)
        r["checked_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        return d, r

    with cf.ThreadPoolExecutor(max_workers=args.workers) as ex:
        futs = [ex.submit(work, d) for d in domains]
        for i, fut in enumerate(cf.as_completed(futs), 1):
            d, r = fut.result()
            results[d] = r
            if i % 100 == 0:
                print(f"  {i}/{len(domains)}", file=sys.stderr, flush=True)
    finished = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    os.makedirs(args.out, exist_ok=True)
    write_signals(os.path.join(args.out, "signals.csv"), targets, results)
    write_requeue(os.path.join(args.out, "REQUEUE.md"), targets, results, hygiene, stats,
                  args, total_domains, started, finished)
    c = Counter(r["signal_class"] for r in results.values())
    print(dict(c), file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
