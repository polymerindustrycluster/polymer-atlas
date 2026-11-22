#!/usr/bin/env python3
"""check_pr_rules: the mechanical half of the working rules adopted 2026-11-22 (AGENTS.md section 2a).

Checks one pull request against rules 1, 4, 5 and 6. Rules 2 and 3 are scripts/check_evidence_binding.py (another
lane). Rule 7 has no check.

Facts come from a JSON file (--facts, testable offline) or are collected live (--pr N, needs git and the gh CLI).
Every rule prints what it inspected and what it could not inspect; anything it could not inspect FAILS the run, so a
silent skip cannot read as a pass. Shortcut limits are named in tasks/working-rules-2026-11-22/README.md.

Usage: python3 scripts/check_pr_rules.py --pr 123 [--base origin/main]
       python3 scripts/check_pr_rules.py --facts facts.json
       python3 scripts/check_pr_rules.py --write-baseline        (regenerate the grandfathered-label list from main)
"""
import argparse
import csv
import io
import json
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
MAX_EVIDENCE_ROWS = 1000  # rule 5: evidence rows one PR may add without a size waiver
MAX_REGISTRY_LINKS = 1000  # rule 5: registry links one PR may add without a size waiver
BASELINE = "tasks/working-rules-2026-11-22/audit_baseline.txt"
FAMILIES = {  # substring of the Verifier / Built-by text -> model family
    "anthropic": "anthropic", "claude": "anthropic", "opus": "anthropic", "sonnet": "anthropic", "haiku": "anthropic",
    "openai": "openai", "codex": "openai", "gpt": "openai",
    "google": "google", "gemini": "google", "antigravity": "google",
    "xai": "xai", "x.ai": "xai", "grok": "xai",
}
RECORD_HEAD = re.compile(r"\A\s*\*\*Review record\*\*", re.I)
VERIFIER = re.compile(r"^\s*[-*]\s*\*\*Verifier:\*\*\s*(.+)$", re.M | re.I)
VERDICT = re.compile(r"^\s*[-*]\s*\*\*Verdict:\*\*\s*(APPROVE|REFUTE)\b[^\n]*?\b([0-9a-f]{40})\b", re.M | re.I)
BUILT_BY = re.compile(r"^Built by:\s*([^,\n]+),\s*(.+?)\s*$", re.M)
SHA_LINE = re.compile(r"^[0-9a-f]{64}  \S.*$")
INPUTS_PATH = re.compile(r"^tasks/[^/]+/INPUTS\.sha256$")


def family_of(text):
    t = text.lower()
    found = {fam for key, fam in FAMILIES.items() if key in t}
    return found.pop() if len(found) == 1 else None  # none or several: cannot classify


def review_records(comments, head_sha):
    """-> (counted, notes). counted = {family: comment index}; notes = lines about records that did not count."""
    counted, notes = {}, []
    for i, body in enumerate(comments):
        if not RECORD_HEAD.match(body or ""):
            continue
        v, d = VERIFIER.search(body), VERDICT.search(body)
        if not v or not d:
            notes.append(f"comment {i}: Review record without a parsable Verifier and Verdict line (not counted)")
            continue
        fam = family_of(v.group(1).split(",")[0])
        if fam is None:
            notes.append(f"comment {i}: verifier family not recognised in {v.group(1)[:60]!r} (not counted)")
        elif d.group(1).upper() != "APPROVE":
            notes.append(f"comment {i}: {fam} verdict {d.group(1).upper()} (not an approval)")
        elif d.group(2).lower() != head_sha.lower():
            notes.append(f"comment {i}: {fam} APPROVE is at {d.group(2)[:8]}, not the head {head_sha[:8]} (stale, not counted)")
        else:
            counted.setdefault(fam, i)
    return counted, notes


def check_review(f, out):
    """Rules 1 and 4. Returns (failures, not_inspected)."""
    fails, blind = [], []
    pr, comments, files = f.get("pr"), f.get("comments"), f.get("changed_files")
    if not pr or not pr.get("head_sha") or pr.get("body") is None or comments is None or files is None:
        return fails, ["PR head SHA, body, comments or changed-file list missing from the facts"]
    data_pr = any(p.startswith(("data/", "scripts/")) for p in files)
    need = 2 if data_pr else 1
    counted, notes = review_records(comments, pr["head_sha"])
    out.append(f"inspected: {len(files)} changed files; {len(comments)} PR comments; head {pr['head_sha'][:8]}")
    out.append(f"  PR touches data/ or scripts/: {data_pr} -> {need} review record(s) from {need} family(ies) required")
    out.extend(f"  note: {n}" for n in notes)
    out.append(f"  counted records (family: comment index): {counted or 'none'}")
    if len(counted) < need:
        fails.append(f"rule 4: {len(counted)} family(ies) approved the current head; {need} required")
    m = BUILT_BY.search(pr["body"])
    if not m:
        fails.append('rule 1: PR body has no line "Built by: <harness>, <model family>"')
    else:
        builder = family_of(m.group(2))
        out.append(f"  builder: {m.group(1).strip()}, {m.group(2).strip()} -> family {builder}")
        if builder is None:
            fails.append(f"rule 1: builder family not recognised in {m.group(2)!r}")
        elif not set(counted) - {builder}:
            fails.append(f"rule 1: no counted reviewer is from a family other than the builder's ({builder})")
    return fails, blind


def check_size(f, out):
    """Rule 5, size cap and the audit-before-next-batch gate."""
    fails, blind = [], []
    for k in ("added_evidence_rows", "added_registry_links", "changed_files", "added_decisions_lines", "pr"):
        if f.get(k) is None:
            blind.append(f"facts missing {k!r}")
    if blind:
        return fails, blind
    ev, rl, files = f["added_evidence_rows"], f["added_registry_links"], f["changed_files"]
    branch = f["pr"].get("branch", "")
    out.append(f"inspected: PR adds {ev} evidence rows (cap {MAX_EVIDENCE_ROWS}) and {rl} registry links (cap {MAX_REGISTRY_LINKS})")
    if ev > MAX_EVIDENCE_ROWS or rl > MAX_REGISTRY_LINKS:
        waiver = [ln for ln in f["added_decisions_lines"] if branch and branch in ln and re.search(r"size waiver", ln, re.I)]
        out.append(f"  size waiver line in DECISIONS.md naming {branch!r}: {'found' if waiver else 'none'}")
        if not waiver:
            fails.append(f"rule 5: over the size cap ({ev} evidence rows, {rl} registry links) and DECISIONS.md adds no "
                         f'line naming the branch and "size waiver"')
    if not any(p.startswith("data/") for p in files):
        out.append("  audit gate: not applicable, the PR touches nothing under data/")
        return fails, blind
    for k in ("main_labels", "baseline_labels", "audit_texts"):
        if f.get(k) is None:
            blind.append(f"facts missing {k!r} (audit gate)")
    if blind:
        return fails, blind
    audited_text = "\n".join(f["audit_texts"].values())
    base = set(f["baseline_labels"])
    unaudited = sorted(
        lab for lab in set(f["main_labels"]) - base
        if not re.search(r"(?<![\w.-])" + re.escape(lab) + r"(?![\w.-])", audited_text))
    out.append(f"  audit gate: {len(f['main_labels'])} created_by labels on main, {len(base)} grandfathered in the baseline, "
               f"{len(f['audit_texts'])} AUDIT.md file(s) on main, {len(unaudited)} unaudited")
    if unaudited:
        fails.append("rule 5: created_by label(s) on main with no tasks/<folder>/AUDIT.md naming them, and not in the "
                     "baseline: " + ", ".join(unaudited[:10]) + (" ..." if len(unaudited) > 10 else ""))
    return fails, blind


def check_inputs(f, out):
    """Rule 6: INPUTS.sha256 present and well-formed when evidence rows or registry links are added."""
    fails, blind = [], []
    for k in ("added_evidence_rows", "added_registry_links", "added_files", "inputs_files"):
        if f.get(k) is None:
            blind.append(f"facts missing {k!r}")
    if blind:
        return fails, blind
    n = f["added_evidence_rows"] + f["added_registry_links"]
    if n == 0:
        out.append("inspected: PR adds no evidence rows or registry links; INPUTS.sha256 not required")
        return fails, blind
    added = [p for p in f["added_files"] if INPUTS_PATH.match(p)]
    out.append(f"inspected: PR adds {n} evidence rows/registry links; INPUTS.sha256 files added: {added or 'none'}")
    if not added:
        fails.append("rule 6: no tasks/<folder>/INPUTS.sha256 added")
    for p in added:
        text = f["inputs_files"].get(p)
        if text is None:
            blind.append(f"could not read added file {p}")
            continue
        lines = [ln for ln in text.splitlines() if ln.strip() and not ln.startswith("#")]
        bad = [ln for ln in lines if not SHA_LINE.match(ln) or ".." in ln.split("  ", 1)[-1].split("/") or ln.split("  ", 1)[-1].startswith("/")]
        out.append(f"  {p}: {len(lines)} entries, {len(bad)} malformed")
        if not lines:
            fails.append(f"rule 6: {p} has no entries")
        if bad:
            fails.append(f'rule 6: {p} has malformed lines (need "<sha256>  <relative path>"): {bad[0][:80]!r}')
    out.append("  format only: the hashes themselves are NOT checked here; a reviewer checks them against the shared store")
    return fails, blind


RULES = (("rules 1 and 4 (review record, builder != reviewer)", check_review),
         ("rule 5 (size cap, audit before the next batch)", check_size),
         ("rule 6 (raw inputs by checksum)", check_inputs))


def run(f, write=print):
    failed = False
    notice = list(f.get("uninspectable") or [])
    if notice:
        write("COULD NOT COLLECT: " + "; ".join(notice))
        failed = True
    for title, fn in RULES:
        out = []
        fails, blind = fn(f, out)
        write(f"== {title}: " + ("FAIL" if fails or blind else "pass"))
        for ln in out:
            write("  " + ln)
        for b in blind:
            write("  NOT INSPECTED (fails the run): " + b)
        for x in fails:
            write("  FAIL: " + x)
        failed = failed or bool(fails or blind)
    write("RESULT: " + ("FAIL" if failed else "pass"))
    return 1 if failed else 0


# ---------------------------------------------------------------- collection (git + gh)
def git(*args):
    return subprocess.run(["git", "-C", str(REPO), *args], capture_output=True, text=True, check=True).stdout


def show(ref, path):
    r = subprocess.run(["git", "-C", str(REPO), "show", f"{ref}:{path}"], capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else None


def rows(text):
    """CSV text -> list of row tuples, header excluded."""
    r = list(csv.reader(io.StringIO(text or "")))
    return [tuple(x) for x in r[1:]], (r[0] if r else [])


def added_rows(base, head, path, key):
    """Rows in `path` at head whose key is absent at base. key=None keys on the whole row."""
    new, hdr = rows(show(head, path))
    old, _ = rows(show(base, path))
    pick = (lambda r, i=hdr.index(key): r[i]) if key else tuple
    seen = {pick(r) for r in old}
    return sum(1 for r in new if pick(r) not in seen)


def labels_at(ref):
    labs = set()
    for p in git("ls-tree", "-r", "--name-only", ref, "--", "data/").split():
        if not p.endswith(".csv"):
            continue
        rs, hdr = rows(show(ref, p))
        if "created_by" in hdr:
            i = hdr.index("created_by")
            labs.update(r[i] for r in rs if len(r) > i and r[i])
    return sorted(labs)


def collect(pr_number, base_ref):
    gh = lambda *a: json.loads(subprocess.run(["gh", *a], capture_output=True, text=True, check=True).stdout)
    f: dict = {"uninspectable": []}
    try:
        meta = gh("pr", "view", str(pr_number), "--json", "headRefOid,headRefName,body,comments")
        f["pr"] = {"number": pr_number, "head_sha": meta["headRefOid"], "branch": meta["headRefName"], "body": meta["body"] or ""}
        f["comments"] = [c["body"] for c in meta["comments"]]
    except (subprocess.CalledProcessError, KeyError, ValueError, FileNotFoundError) as e:
        f["uninspectable"].append(f"gh pr view failed: {e}")
        return f
    head = meta["headRefOid"]
    try:
        git("cat-file", "-e", head + "^{commit}")
        base = git("merge-base", base_ref, head).strip()
        names = git("diff", "--name-status", "--no-renames", f"{base}...{head}").splitlines()
        f["changed_files"] = [n.split("\t", 1)[1] for n in names]
        f["added_files"] = [n.split("\t", 1)[1] for n in names if n.startswith("A")]
        ev = [p for p in f["changed_files"] if re.fullmatch(r"data/evidence_[^/]+\.csv", p)]
        f["added_evidence_rows"] = sum(added_rows(base, head, p, "evidence_id") for p in ev)
        f["added_registry_links"] = added_rows(base, head, "data/registry_links.csv", None) if "data/registry_links.csv" in f["changed_files"] else 0
        dec = git("diff", "-U0", f"{base}...{head}", "--", "DECISIONS.md")
        f["added_decisions_lines"] = [ln[1:] for ln in dec.splitlines() if ln.startswith("+") and not ln.startswith("+++")]
        f["inputs_files"] = {p: show(head, p) for p in f["added_files"] if INPUTS_PATH.match(p)}
        if any(p.startswith("data/") for p in f["changed_files"]):
            f["main_labels"] = labels_at(base_ref)
            b = show(base_ref, BASELINE)
            if b is None:
                f["uninspectable"].append(f"{BASELINE} is not on {base_ref}")
            else:
                f["baseline_labels"] = [ln for ln in b.splitlines() if ln.strip() and not ln.startswith("#")]
            f["audit_texts"] = {p: show(base_ref, p) or "" for p in git("ls-tree", "-r", "--name-only", base_ref, "--", "tasks/").split()
                                if re.fullmatch(r"tasks/[^/]+/AUDIT\.md", p)}
    except subprocess.CalledProcessError as e:
        f["uninspectable"].append(f"git failed: {' '.join(e.cmd[3:6])}: {(e.stderr or '').strip()[:120]}")
    return f


def write_baseline(ref):
    labs = labels_at(ref)
    sha = git("rev-parse", ref).strip()
    (REPO / BASELINE).write_text(
        f"# created_by labels present on {ref} at {sha}: grandfathered, no AUDIT.md needed (rule 5).\n"
        "# Generated by: python3 scripts/check_pr_rules.py --write-baseline. Never hand-edit; the check reads it from main.\n"
        + "\n".join(labs) + "\n")
    print(f"wrote {len(labs)} labels to {BASELINE}")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--facts")
    ap.add_argument("--pr", type=int)
    ap.add_argument("--base", default="origin/main")
    ap.add_argument("--write-baseline", action="store_true")
    a = ap.parse_args(argv)
    if a.write_baseline:
        return write_baseline(a.base) or 0
    if a.facts:
        return run(json.loads(Path(a.facts).read_text()))
    if a.pr:
        return run(collect(a.pr, a.base))
    ap.error("give --facts, --pr or --write-baseline")


if __name__ == "__main__":
    sys.exit(main())
