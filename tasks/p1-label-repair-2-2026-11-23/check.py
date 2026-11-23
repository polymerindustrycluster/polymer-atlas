#!/usr/bin/env python3
"""Replay the three coordinated repairs against the selected data base."""
import argparse
from collections import Counter, defaultdict
import hashlib
import io
from pathlib import Path
import runpy
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
LABEL = HERE.name
URL = "p1-url-spaces-2026-11-23"
WEB = "p1-website-placeholders-2026-11-23"
PERSIST = Path.home() / ".bb/thread-storage/thr_9i2c6byhcz/2026-11-06-atlas/persist"
STORE = Path("/Volumes/johnpswan/work/GAC/polymer-atlas/atlas-store")
CLAIMS = ("table", "record_id", "field", "verdict", "evidence_id")
KEYS = {"organizations": "org_id", "sites": "site_id", "people": "person_id", "ecosystem": "org_id", "events": "event_id"}
MARKERS = {"ORG-001689", "ORG-001692", "ORG-001706", "ORG-001710", "ORG-001712"}
UNASSESSED = {"ORG-001961", "ORG-001990", "ORG-002016", "ORG-002036"}
DEAD = {
    "ORG-001971": ("odm.com", "parked"),
    "ORG-002064": ("polytechmolding.com", "404, not this firm's site"),
}

lib = runpy.run_path(str(HERE.parent / "p1-atlas8-corrections-2026-11-23/check.py"))
git, require, parse, csv_bytes, sha = (lib[k] for k in ("git", "require", "parse", "csv_bytes", "sha"))


def path_at(at, path):
    return git("show", f"{at}:{path}") if at else (ROOT / path).read_bytes()


def task_bytes(at, folder, name):
    return path_at(at, f"tasks/{folder}/{name}")


def verify_packet(at, root, name):
    folder = root / name
    manifest = task_bytes(at, name, "PACKET.sha256")
    require(manifest == (folder / "SHA256SUMS").read_bytes(), f"{name}: packet seal differs")
    for line in manifest.decode().splitlines():
        digest, path = line.split("  ", 1)
        require(sha((folder / path).read_bytes()) == digest, f"{name}/{path}: hash differs")
    return folder


def edits_at(base, at, persist, store):
    label, url, web = (verify_packet(at, persist, n) for n in (LABEL, URL, WEB))
    pin = task_bytes(at, WEB, "RULING.md")
    require(pin == (persist / f"{WEB}.RULING.md").read_bytes(), "Website placeholder ruling differs")
    files = list(parse((label / "store-inputs.csv").read_bytes()))
    expected_manifest = {r["landed_sha256"]: f"provenance/label-repair-2-2026-11-23/{r['landed_sha256']}" for r in files}
    manifest = dict(line.split("  ", 1) for line in task_bytes(at, LABEL, "INPUTS.sha256").decode().splitlines())
    require(manifest == expected_manifest and len(manifest) == 4, "Landed provenance manifest differs")
    for digest, path in manifest.items():
        with (store / path).open("rb") as body:
            require(hashlib.file_digest(body, "sha256").hexdigest() == digest, f"{path}: landed body differs")

    ul, wl = (runpy.run_path(str(p / "check.py")) for p in (url, web))
    ul["self_test"]()
    wl["self_test"]()
    url_edits, url_holds, _ = ul["compute"](ROOT, base)
    web_edits, web_holds, web_blanks, _ = wl["compute"](ROOT, base)
    edits = {}
    ledger = defaultdict(list)

    def add(folder, key, old, new, verdict="corrected"):
        require(key not in edits and (old is None or old != new), f"{key}: duplicate or no-op repair")
        edits[key] = old, new
        ledger[folder].append(dict(zip(CLAIMS, (*key, verdict, ""))))

    for folder, path, scan, verifier in ((LABEL, label, None, None), (URL, url, url_edits, ul["verify_edit"]),
                                          (WEB, web, web_edits, wl["verify_edit"])):
        rows = list(parse((path / "edits.csv").read_bytes()))
        keys = {tuple(r[k] for k in CLAIMS[:3]) for r in rows}
        require(len(rows) == len(keys) == {LABEL: 151, URL: 30, WEB: 5}[folder],
                f"{folder}: proposal count differs")
        if scan is not None:
            require(keys == scan.keys(), f"{folder}: fresh scan edit set differs")
        for r in rows:
            key = tuple(r[k] for k in CLAIMS[:3])
            old, new = r["old"], r["new"]
            if scan is not None:
                require((old, new) == scan[key][:2], f"{key}: fresh scan differs from sealed repair")
                if folder == URL:
                    verifier(old, new, key[2] in ul["FIELDS"][key[0]][2])
                else:
                    verifier(old, new)
            elif (key[0], key[2]) not in {("organizations", "naics_primary_source_name"), ("organizations", "description_1line"),
                                         ("events", "subject_note"), ("events", "geography_note")}:
                raise SystemExit(f"{key}: outside label scope")
            add(folder, key, old, new)

    holds = list(parse((url / "holds.csv").read_bytes()))
    require(url_holds == {tuple(r[k] for k in (*CLAIMS[:3], "value")): r["reason"] for r in holds}
            and len(url_holds) == 3, "URL hold census differs")
    holds = list(parse((web / "holds.csv").read_bytes()))
    require(web_holds == {tuple(r[k] for k in CLAIMS[:3]): (r["value"], r["reason"]) for r in holds}
            and len(web_holds) == 6, "Website hold census differs")

    blanks = list(parse((web / "blank_if_ruled.csv").read_bytes()))
    require(len(blanks) == 9 and web_blanks.keys() == {("organizations", rid, "website") for rid in MARKERS | UNASSESSED},
            "Ruling or initial website classification differs")
    for r in blanks:
        key = tuple(r[k] for k in CLAIMS[:3])
        require((r["old"], r["class"]) == web_blanks[key][:2], f"{key}: placeholder witness differs")
        new = "none_found" if key[1] in MARKERS else ""
        add(WEB, key, r["old"], new, "corrected" if new else "withdrawn")

    for rid, (domain, reason) in DEAD.items():
        key = ("organizations", rid, "website")
        old, _ = web_holds.pop(key)
        require(old.startswith((domain, f"https://{domain}")), f"{rid}: retired domain differs")
        add(WEB, key, old, "", "withdrawn")
        add(WEB, ("organizations", rid, "notes"), None, f"website {domain} not used: {reason} as read 2026-11-23")

    remain_url = {k: reason for k, reason in url_holds.items() if k[:3] not in edits}
    require(len(remain_url) == 1 and len(web_holds) == 4, "Remaining URL and website holds differ")
    require(len(edits) == 199 and Counter(row["verdict"] for rows in ledger.values() for row in rows) ==
            {"corrected": 193, "withdrawn": 6}, "Combined claim census differs")
    artifacts = {
        f"tasks/{folder}/CLAIMS_CHECKED.csv": csv_bytes(sorted(rows, key=lambda r: tuple(r[k] for k in CLAIMS[:3])), CLAIMS)
        for folder, rows in ledger.items()
    }
    hold_header = (*CLAIMS[:3], "reason")
    for folder, holds in ((URL, {k[:3]: v for k, v in remain_url.items()}),
                          (WEB, {k: reason for k, (_, reason) in web_holds.items()})):
        artifacts[f"tasks/{folder}/OPEN_QUEUE.csv"] = csv_bytes(
            (dict(zip(hold_header, (*key, why))) for key, why in sorted(holds.items())), hold_header)
    return edits, artifacts, (ul, set(remain_url)), (wl, set(web_holds))


def expected_files(base, edits):
    by_row = defaultdict(dict)
    for (table, rid, field), pair in edits.items():
        by_row[table, rid][field] = pair
    seen, data = set(), {}
    for path in git("ls-tree", "-r", "--name-only", base, "data").decode().splitlines():
        if path.count("/") != 1 or not path.endswith(".csv"):
            continue
        table = Path(path).stem
        if table.startswith(("organizations_", "sites_")):
            table = table.split("_", 1)[0]
        if table not in KEYS:
            continue
        raw = git("show", f"{base}:{path}")
        lines = list(io.StringIO(raw.decode(), newline=""))
        rd = parse(raw)
        output, end, changed = [lines[0].encode()], 1, False
        for row in rd:
            key = table, row[KEYS[table]]
            prior, end = end, rd.line_num
            cells = by_row.get(key)
            if not cells:
                output.append("".join(lines[prior:end]).encode())
                continue
            require(key not in seen, f"{key}: duplicate record")
            seen.add(key)
            changed = True
            for field, (old, new) in cells.items():
                if old is None:
                    require(field == "notes" and new not in row[field], f"{key}: notes already contain the disposition")
                    row[field] = f"{row[field]}; {new}" if row[field] else new
                else:
                    require(row[field] == old, f"{key}/{field}: held field differs from reviewed old cell")
                    row[field] = new
            output.append(csv_bytes([row], rd.fieldnames, with_header=False))
        if changed:
            data[path] = b"".join(output)
    require(seen == by_row.keys(), "A repair key is absent from the base")
    return data


def render(at, url_check, web_check):
    u, url_holds = url_check
    w, web_holds = web_check
    with tempfile.TemporaryDirectory() as tmp:
        subprocess.run(["tar", "-x", "-C", tmp], input=git("archive", at, "data"), check=True)
        data = Path(tmp) / "data"
        require(not u["leftovers"](data, url_holds), "Unclassified spaces remain in candidate URLs")
        require(not w["leftovers"](data, web_holds, set()), "Unclassified website values remain")
        u["ahfa_pages"](ROOT, at, data)
        probes = ["ORG-001543", *sorted(MARKERS), *sorted(UNASSESSED), *DEAD]
        pages = w["render"](ROOT, at, data, probes)
        require("https://hammillmedical.com/" in pages["ORG-001543"] and "hammillmedical.com;" not in pages["ORG-001543"],
                "Corrected organization link did not render")
        require(all(pages[rid] == "No website found" for rid in MARKERS), "Website marker did not render")
        require(all(pages[rid] == "(no Website row)" for rid in UNASSESSED | DEAD.keys()),
                "Cleared website value rendered")
    print("PASS built pages: three AHFA sources, one corrected website link, five markers and six cleared website fields")


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("--at", default="HEAD")
    cli.add_argument("--base")
    cli.add_argument("--persist", type=Path, default=PERSIST)
    cli.add_argument("--store", type=Path, default=STORE)
    cli.add_argument("--apply-backup", type=Path)
    cli.add_argument("--render", action="store_true")
    a = cli.parse_args()
    base = a.base or git("merge-base", a.at, "origin/main").decode().strip()
    edits, artifacts, url_check, web_check = edits_at(base, None if a.apply_backup else a.at, a.persist, a.store)
    data = expected_files(base, edits)
    if a.apply_backup:
        a.apply_backup.mkdir(parents=True, exist_ok=True)
        for path, content in data.items():
            before = git("show", f"{base}:{path}")
            backup = a.apply_backup / Path(path).name
            require((ROOT / path).read_bytes() in (before, content), f"{path}: unrelated changes present")
            require(not backup.exists() or backup.read_bytes() == before, f"{path}: backup differs")
            backup.write_bytes(before)
        for path, content in {**data, **artifacts}.items():
            (ROOT / path).write_bytes(content)
    else:
        delta = set(git("diff", "--name-only", base, a.at, "--", "data").decode().splitlines())
        require(delta == data.keys(), "Unexpected changed data paths")
        for path, content in {**data, **artifacts}.items():
            require(path_at(a.at, path) == content, f"{path}: applied bytes differ")
        if a.render:
            render(a.at, url_check, web_check)
    print("PASS: 199 changed cells across three packets (193 corrected, 6 withdrawn); 1 URL hold and 4 website holds")


if __name__ == "__main__":
    main()
