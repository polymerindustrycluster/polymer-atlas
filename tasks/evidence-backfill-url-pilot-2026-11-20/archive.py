#!/usr/bin/env python3
"""Archive at capture (SCHEMA §4.22, V-66) for this lane's applied rows: a Wayback capture of each cited page, admitted
only if the capture replays and still contains the row's quote. Writes archive_rows.csv (admitted) and
archive_held.csv (with the reason); apply_archive appends admitted rows to data/archive_links.csv.

  python3 tasks/evidence-backfill-url-pilot-2026-11-20/archive.py capture <corpus>   # live: availability, Save Page Now, replay
  python3 tasks/evidence-backfill-url-pilot-2026-11-20/archive.py apply .            # append admitted rows to data/
Results per URL are cached as JSON under <corpus>/archive/ so a rerun makes no new requests. Stdlib only.
"""
import csv, gzip, hashlib, html, json, re, sys, time, urllib.error, urllib.parse, urllib.request, zlib
from pathlib import Path

HERE = Path(__file__).resolve().parent
UA = {"User-Agent": "research-client/1.0", "Accept-Encoding": "identity"}
CREATED_BY = "claude-code-evd-backfill-url-pilot"
FIELDS = ["evidence_id", "archive_ref", "captured_at", "created_by"]


def decode(raw, encoding):
    # Wayback id_ replays serve the archived bytes as stored, often still gzip/deflate-encoded whatever we ask for
    enc = (encoding or "").lower()
    if "gzip" in enc or raw[:2] == b"\x1f\x8b":
        raw = gzip.decompress(raw)
    elif "deflate" in enc:
        raw = zlib.decompress(raw, -zlib.MAX_WBITS)
    elif "br" in enc:  # shortcut: no stdlib brotli; such a capture is held, never admitted unread
        return None
    return raw.decode("utf-8", "replace")


def get(url, timeout=90):
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=timeout) as r:
            return r.status, decode(r.read(3_000_000), r.headers.get("Content-Encoding"))
    except urllib.error.HTTPError as e:
        return e.code, ""
    except Exception as e:  # network failure is an availability signal, never a verdict
        return 0, type(e).__name__


def latest_capture(url):
    code, body = get("https://web.archive.org/cdx/search/cdx?" + urllib.parse.urlencode(
        {"url": url, "output": "json", "limit": "-1", "fl": "timestamp,statuscode", "filter": "statuscode:200"}))
    rows = json.loads(body)[1:] if code == 200 and body.strip().startswith("[") else []
    return rows[-1][0] if rows else None


def norm(s):
    return re.sub(r"[^a-z0-9]+", "", html.unescape(s).lower())


def page_text(raw):
    return re.sub(r"<[^>]+>", " ", re.sub(r"(?is)<(script|style|noscript).*?</\1>", " ", raw))


def capture(url, cache):
    """The capture timestamp is cached (no second Save Page Now); the replay is re-read on every run."""
    f = cache / (hashlib.sha1(url.encode()).hexdigest()[:16] + ".json")
    rec = json.loads(f.read_text(encoding="utf-8")) if f.exists() else {"url": url, "timestamp": latest_capture(url)}
    ts = rec["timestamp"]
    if not ts or ts[:8] < "20261120":  # archive at capture: a capture made now, not an old one (retried until fresh)
        get("https://web.archive.org/save/" + url, timeout=180)
        for _ in range(6):
            time.sleep(20)
            ts = latest_capture(url)
            if ts and ts[:8] >= "20261120":
                break
        rec["timestamp"] = ts
    f.write_text(json.dumps({"url": url, "timestamp": rec["timestamp"]}), encoding="utf-8")
    if ts and ts[:8] >= "20261120":
        code, raw = get(f"https://web.archive.org/web/{ts}id_/{url}")
        rec.update(replay_status=code if raw is not None else "brotli-unread",
                   replay_norm=norm(page_text(raw)) if code == 200 and raw else "")
    return rec


def quote_found(quote, replay_norm):
    """Word-level: >= 80% of the quote's 4+-letter words occur in the capture (text order differs between extractors)."""
    words = {w.lower() for w in re.findall(r"[A-Za-z][A-Za-z0-9]{3,}", html.unescape(quote))}
    return bool(words) and sum(norm(w) in replay_norm for w in words) / len(words) >= 0.8


def main():
    mode, arg = sys.argv[1], Path(sys.argv[2])
    if mode == "capture":
        cache = arg / "archive"
        cache.mkdir(parents=True, exist_ok=True)
        rows = [r for p in ("applied.csv", "applied_round2.csv") for r in csv.DictReader(open(HERE / p, encoding="utf-8"))]
        admitted, held = [], []
        for r in sorted(rows, key=lambda r: r["evidence_id"]):
            rec = capture(r["source_ref"], cache)
            quote = r["claim_detail"].split("quote:", 1)[1].strip() if "quote:" in r["claim_detail"] else ""
            ts = rec.get("timestamp")
            if not ts or ts[:8] < "20261120":
                held.append({**r, "held": "no fresh Wayback capture"})
            elif rec.get("replay_status") != 200:
                held.append({**r, "held": f"capture does not replay ({rec.get('replay_status')})"})
            elif not quote_found(quote, rec["replay_norm"]):
                held.append({**r, "held": "quote absent from the capture"})
            else:
                admitted.append({"evidence_id": r["evidence_id"], "archive_ref": f"https://web.archive.org/web/{ts}/{r['source_ref']}",
                                 "captured_at": f"{ts[:4]}-{ts[4:6]}-{ts[6:8]}", "created_by": CREATED_BY})
        with open(HERE / "archive_rows.csv", "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=FIELDS, lineterminator="\n"); w.writeheader(); w.writerows(admitted)
        with open(HERE / "archive_held.csv", "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=["evidence_id", "source_ref", "held"], extrasaction="ignore", lineterminator="\n")
            w.writeheader(); w.writerows(held)
        print(f"admitted {len(admitted)}, held {len(held)} of {len(rows)} rows")
    elif mode == "apply":
        target = arg / "data" / "archive_links.csv"
        have = {r["evidence_id"] for r in csv.DictReader(open(target, encoding="utf-8"))}
        new = [r for r in csv.DictReader(open(HERE / "archive_rows.csv", encoding="utf-8")) if r["evidence_id"] not in have]
        assert all(r["evidence_id"] > max(have) for r in new), "would break ascending evidence_id order"
        with open(target, "a", newline="", encoding="utf-8") as fh:
            csv.DictWriter(fh, fieldnames=FIELDS, lineterminator="\n").writerows(new)
        print(f"appended {len(new)} archive_links rows")


if __name__ == "__main__":
    main()
