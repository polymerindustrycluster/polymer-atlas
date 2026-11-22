#!/usr/bin/env python3
"""check_pr_rules: the mechanical half of the working rules adopted 2026-11-22 (AGENTS.md section 2a).

Checks one pull request against rules 1, 4, 5 and 6. Rules 2 and 3 are scripts/check_evidence_binding.py (another
lane). Rule 7 has no check.

Facts come from a JSON file (--facts, testable offline) or are collected live (--pr N, needs git and the gh CLI).
Every rule prints what it inspected and what it could not inspect; anything it could not inspect FAILS the run, so a
silent skip cannot read as a pass. A failed read of a tracked git object is an inspection failure; only a path absent
from one side of the diff counts as absent. Shortcut limits are in tasks/working-rules-2026-11-22/README.md.

In CI the workflow runs the copy of this file on the base branch (pull_request_target), never the PR's own copy, and
--post publishes the result as the check run `pr-rules` on the PR head.

--publish-gate posts the binding-gate job of the same workflow as the check run `binding-gate`.

Usage: python3 scripts/check_pr_rules.py --pr 123 [--post]
       python3 scripts/check_pr_rules.py --publish-gate DIR --pr 123
       python3 scripts/check_pr_rules.py --facts facts.json
       python3 scripts/check_pr_rules.py --write-baseline        (regenerate the grandfathered-label list from main)
"""
import argparse
import csv
import io
import json
import os
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
MAX_EVIDENCE_ROWS = 1000  # rule 5: evidence rows one PR may add without a size waiver
MAX_REGISTRY_LINKS = 1000  # rule 5: registry links one PR may add without a size waiver
BASELINE = "tasks/working-rules-2026-11-22/audit_baseline.txt"
TWO_FAMILY_PATHS = ("data/",)  # tier by risk (owner ruling 2026-11-22): data/ needs two families, every other PR one
REGISTRY_IDENTITY = ("org_id", "registry", "registry_id", "site_id")  # SCHEMA 4.8 grain; match_basis, as_of are metadata
MODEL_FAMILY = (  # fixed map, matched on whole words of the model name (and of "Built by" text); owner ruling 2026-11-22
    ("gpt", "openai"), ("codex", "openai"), ("openai", "openai"),
    ("claude", "anthropic"), ("opus", "anthropic"), ("sonnet", "anthropic"), ("haiku", "anthropic"),
    ("fable", "anthropic"), ("anthropic", "anthropic"),
    ("gemini", "google"), ("google", "google"), ("grok", "xai"), ("xai", "xai"), ("muse", "meta"), ("meta", "meta"))
RECORD_HEAD = re.compile(r"\A\s*\*\*Review record\*\*", re.I)
VERIFIER = re.compile(r"^\s*[-*]\s*\*\*Verifier:\*\*\s*(.+)$", re.M | re.I)
# the verdict word, then optionally "at <40 hex>" immediately: an abbreviated SHA, or a SHA mentioned later, is no SHA
VERDICT = re.compile(r"^\s*[-*]\s*\*\*Verdict:\*\*\s*(APPROVE|REFUTE)\b(?:\s+at\s+`?([0-9a-f]{40})(?![0-9a-f]))?", re.M | re.I)
CHECKED = re.compile(r"^\s*[-*]\s*\*\*What it checked:\*\*\s*(\S.{9,})$", re.M | re.I)
BUILT_BY = re.compile(r"^Built by:\s*([^,\n]+),\s*(.+?)\s*$", re.M)
SHA_LINE = re.compile(r"^([0-9a-f]{64})  (\S.*)$")
INPUTS_PATH = re.compile(r"^tasks/[^/]+/INPUTS\.sha256$")
AUDIT_PATH = re.compile(r"^tasks/[^/]+/AUDIT\.md$")


class InspectionError(Exception):
    """A tracked object could not be read, or a file is not what the check needs: the run must fail, not pass."""


def family_of(text):
    t = text.lower()
    found = {fam for kw, fam in MODEL_FAMILY if re.search(r"(?<![a-z])" + re.escape(kw) + r"(?![a-z])", t)}
    return found.pop() if len(found) == 1 else None  # none or several: cannot classify


def review_votes(comments):
    """Every Review record with a known verifier -> latest vote per verifier (model). Returns (votes, notes).
    votes[model_key] = dict(fam, verdict, sha, complete, idx). The latest record per verifier governs."""
    votes, notes = {}, []
    for i, body in enumerate(comments):
        if not RECORD_HEAD.match(body or ""):
            continue
        v, d = VERIFIER.search(body), VERDICT.search(body)
        parts = [x.strip() for x in v.group(1).split(",")] if v else []
        fam = family_of(parts[1]) if len(parts) > 1 else None
        if not d:
            notes.append(f"comment {i}: Review record without a Verdict line (not counted)")
        elif fam is None:
            notes.append(f"comment {i}: no recognised model in the Verifier line {(v.group(1)[:60] if v else '')!r}; "
                         "need '<harness>, <model>, ...' (not counted)")
        else:
            key = re.sub(r"\s+", " ", parts[1].lower())
            checked = bool(CHECKED.search(body))
            if d.group(1).upper() == "REFUTE" and not re.search(r"\bBLOCKING\b", body):
                notes.append(f"comment {i}: REFUTE without a BLOCKING finding (does not follow the tier rule; still withdraws)")
            if not checked:
                notes.append(f"comment {i}: no 'What it checked' line of substance (cannot count as an approval)")
            votes[key] = dict(fam=fam, verdict=d.group(1).upper(), sha=(d.group(2) or "").lower(), complete=checked, idx=i)
    return votes, notes


def counted_families(comments, head_sha):
    """-> ({family: [model, ...]}, notes). A family counts when one of its verifiers' latest vote is a complete APPROVE
    at exactly the head SHA and none of its verifiers' latest vote is a REFUTE (at the head or at no SHA)."""
    votes, notes = review_votes(comments)
    ok, blocked = {}, set()
    for key, vt in votes.items():
        if vt["verdict"] == "REFUTE":
            if vt["sha"] in ("", head_sha.lower()):
                blocked.add(vt["fam"])
                notes.append(f"comment {vt['idx']}: {key} REFUTE at the head withdraws {vt['fam']}")
            else:
                notes.append(f"comment {vt['idx']}: {key} REFUTE at an older SHA (its latest vote; not an approval)")
        elif not vt["sha"]:
            notes.append(f"comment {vt['idx']}: {key} APPROVE without a full 40-character SHA (not counted)")
        elif vt["sha"] != head_sha.lower():
            notes.append(f"comment {vt['idx']}: {key} APPROVE is at {vt['sha'][:8]}, not the head {head_sha[:8]} (stale, not counted)")
        elif vt["complete"]:
            ok.setdefault(vt["fam"], []).append(key)
    return {fam: m for fam, m in ok.items() if fam not in blocked}, notes


def check_review(f, out):
    """Rules 1 and 4. Returns (failures, not_inspected)."""
    fails, blind = [], []
    pr, comments, files = f.get("pr"), f.get("comments"), f.get("changed_files")
    if not pr or not pr.get("head_sha") or pr.get("body") is None or comments is None or files is None:
        return fails, ["PR head SHA, body, comments or changed-file list missing from the facts"]
    if not files:
        return fails, ["the PR's changed-file list is empty: cannot tell what the PR touches"]
    two = any(p.startswith(TWO_FAMILY_PATHS) for p in files)
    need = 2 if two else 1
    counted, notes = counted_families(comments, pr["head_sha"])
    out.append(f"inspected: {len(files)} changed files; {len(comments)} PR comments; head {pr['head_sha'][:8]}")
    out.append(f"  PR touches data/: {two} -> {need} family(ies) required")
    out.extend(f"  note: {n}" for n in notes)
    out.append(f"  counted (family: models): {counted or 'none'}")
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


def _field(text, name):
    return [m.group(1).strip() for m in re.finditer(
        r"^\s*(?:[-*]\s*)?(?:\*\*)?" + name + r":(?:\*\*)?[ \t]*(\S[^\n]*?)[ \t]*$", text, re.M | re.I)]


def parse_audit(text):
    """-> (labels, result, why_not). An AUDIT.md counts only with Label:, Result: PASS|FAIL, Sample: and Reviewers:."""
    labels = {x.strip() for v in _field(text, "Label") for x in v.split(";") if x.strip()}
    results = {v.upper() for v in _field(text, "Result")}
    if not labels:
        return set(), None, "no Label: line"
    if len(results) != 1 or not results <= {"PASS", "FAIL"}:
        return labels, None, f"Result: must be exactly PASS or FAIL (found {sorted(results) or 'none'})"
    if not _field(text, "Sample"):
        return labels, None, "no Sample: line"
    if not _field(text, "Reviewers"):
        return labels, None, "no Reviewers: line"
    return labels, results.pop(), None


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
        naming = r"(?<![\w/.-])" + re.escape(branch) + r"(?![\w/.-])"
        waiver = [ln for ln in f["added_decisions_lines"] if branch and re.search(naming, ln) and re.search(r"size waiver", ln, re.I)]
        out.append(f"  size waiver line added to DECISIONS.md naming exactly {branch!r}: {'found' if waiver else 'none'}")
        if not waiver:
            fails.append(f"rule 5: over the size cap ({ev} evidence rows, {rl} registry links) and the PR adds no DECISIONS.md "
                         f'line naming exactly its branch and the words "size waiver"')
    if not any(p.startswith("data/") for p in files):
        out.append("  audit gate: not applicable, the PR touches nothing under data/")
        return fails, blind
    for k in ("main_labels", "baseline_labels", "audit_texts"):
        if f.get(k) is None:
            blind.append(f"facts missing {k!r} (audit gate)")
    if blind:
        return fails, blind
    passed, failed = set(), set()
    for path, text in sorted(f["audit_texts"].items()):
        labels, result, why = parse_audit(text or "")
        if why:
            out.append(f"  ignored {path}: {why}")
        elif result == "PASS":
            passed |= labels
        else:
            failed |= labels
    main_labels, base = set(f["main_labels"]), set(f["baseline_labels"])
    unaudited = sorted((main_labels - base) - passed - failed)
    failing = sorted(main_labels & failed)
    out.append(f"  audit gate: {len(main_labels)} created_by labels on main, {len(base)} grandfathered in the baseline, "
               f"{len(f['audit_texts'])} AUDIT.md file(s) on main, {len(unaudited)} unaudited, {len(failing)} with a FAIL audit")
    if unaudited:
        fails.append("rule 5: created_by label(s) on main with no valid PASS tasks/<folder>/AUDIT.md and not in the "
                     "baseline: " + ", ".join(unaudited[:10]) + (" ..." if len(unaudited) > 10 else ""))
    if failing:
        fails.append("rule 5: created_by label(s) on main whose AUDIT.md says Result: FAIL: " + ", ".join(failing[:10]))
    return fails, blind


def valid_input_path(p):
    """A relative POSIX file path: no absolute form (either style), no '.' or '..' component, no trailing slash."""
    if not p or p != p.strip() or "\\" in p or p.startswith("/") or re.match(r"^[A-Za-z]:", p) or p.endswith("/"):
        return False
    return not any(c in ("", ".", "..") for c in p.split("/")) and not re.search(r"[\x00-\x1f]", p)


def inputs_entries(text):
    return [ln for ln in (text or "").splitlines() if ln.strip() and not ln.startswith("#")]


def in_store(path):
    return path.split("/")[0] in ("raw", "provenance")


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
        lines = inputs_entries(text)
        bad = []
        for ln in lines:
            m = SHA_LINE.match(ln)
            if not m or not valid_input_path(m.group(2)):
                bad.append(ln)
            elif not in_store(m.group(2)):
                ok = (f.get("inputs_repo_ok") or {}).get(m.group(2))
                if ok is None:
                    blind.append(f"{p}: whether repo path {m.group(2)!r} is an existing file was not collected")
                elif not ok:
                    bad.append(ln)
        out.append(f"  {p}: {len(lines)} entries, {len(bad)} malformed or not a file under raw/, provenance/ or in the repo")
        if not lines:
            fails.append(f"rule 6: {p} has no entries")
        if bad:
            fails.append(f'rule 6: {p} has bad lines (need "<sha256>  <relative file path under raw/, provenance/ or an '
                         f'existing repo file>"): {bad[0][:80]!r}')
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
def _git(*args):
    return subprocess.run(["git", "-C", str(REPO), *args], capture_output=True, text=True, errors="replace")


def git(*args):
    r = _git(*args)
    if r.returncode:
        raise InspectionError(f"git {' '.join(args[:3])} failed: {r.stderr.strip()[:120]}")
    return r.stdout


def show(ref, path):
    """Text of `path` at `ref`. None only when the path is absent at ref; a failed read of a present path raises."""
    if not git("ls-tree", ref, "--", path).strip():
        return None
    return git("show", f"{ref}:{path}")


def rows(text):
    """CSV text -> (list of row tuples, header). Short rows are an inspection failure, not a skipped row."""
    r = list(csv.reader(io.StringIO(text or "")))
    hdr = r[0] if r else []
    for x in r[1:]:
        if len(x) < len(hdr):
            raise InspectionError(f"row with {len(x)} fields under a {len(hdr)}-field header")
    return [tuple(x) for x in r[1:]], hdr


def keys_at(ref, path, cols):
    """Set of identity tuples of `path` at `ref`; empty when the file is absent at ref."""
    text = show(ref, path)
    if text is None:
        return set()
    rs, hdr = rows(text)
    missing = [c for c in cols if c not in hdr]
    if missing:
        raise InspectionError(f"{path} at {ref[:12]} lacks column(s) {missing}")
    idx = [hdr.index(c) for c in cols]
    return {tuple(r[i] for i in idx) for r in rs}


def added_rows(base, head, path, cols):
    """Identities in `path` at head absent at base. A metadata edit to a held identity is not an added row."""
    return len(keys_at(head, path, cols) - keys_at(base, path, cols))


def labels_at(ref):
    labs = set()
    for p in filter(None, git("ls-tree", "-r", "-z", "--name-only", ref, "--", "data/").split("\0")):
        if p.endswith(".csv"):
            rs, hdr = rows(show(ref, p))
            if "created_by" in hdr:
                i = hdr.index("created_by")
                labs.update(r[i] for r in rs if r[i])
    return sorted(labs)


def gh_json(*args):
    return json.loads(subprocess.run(["gh", *args], capture_output=True, text=True, check=True).stdout)


def collect(pr_number, base_ref=None):
    f: dict = {"uninspectable": []}
    try:
        meta = gh_json("pr", "view", str(pr_number), "--json", "headRefOid,headRefName,baseRefName,body,comments")
        f["pr"] = {"number": pr_number, "head_sha": meta["headRefOid"], "branch": meta["headRefName"], "body": meta["body"] or ""}
        f["comments"] = [c["body"] for c in meta["comments"]]
    except (subprocess.CalledProcessError, KeyError, ValueError, FileNotFoundError) as e:
        f["uninspectable"].append(f"gh pr view failed: {e}")
        return f
    head, base_ref = meta["headRefOid"], base_ref or f"origin/{meta['baseRefName']}"
    try:
        if _git("cat-file", "-e", head + "^{commit}").returncode:  # data only: fetching never runs PR code
            git("fetch", "--no-tags", "-q", "origin", f"+refs/pull/{pr_number}/head:refs/remotes/pr/{pr_number}")
        git("cat-file", "-e", head + "^{commit}")
        base = git("merge-base", base_ref, head).strip()
        toks = git("diff", "--name-status", "-z", "--no-renames", f"{base}...{head}").split("\0")
        pairs = list(zip(toks[0::2], toks[1::2]))
        f["changed_files"] = [p for _, p in pairs]
        f["added_files"] = [p for st, p in pairs if st == "A"]
        ev = [p for p in f["changed_files"] if re.fullmatch(r"data/evidence_[^/]+\.csv", p)]
        f["added_evidence_rows"] = sum(added_rows(base, head, p, ("evidence_id",)) for p in ev)
        f["added_registry_links"] = added_rows(base, head, "data/registry_links.csv", REGISTRY_IDENTITY) \
            if "data/registry_links.csv" in f["changed_files"] else 0
        dec = git("diff", "-U0", f"{base}...{head}", "--", "DECISIONS.md")
        f["added_decisions_lines"] = [ln[1:] for ln in dec.splitlines() if ln.startswith("+") and not ln.startswith("+++")]
        f["inputs_files"] = {p: show(head, p) for p in f["added_files"] if INPUTS_PATH.match(p)}
        f["inputs_repo_ok"] = {}
        for text in f["inputs_files"].values():
            for ln in inputs_entries(text):
                m = SHA_LINE.match(ln)
                if m and valid_input_path(m.group(2)) and not in_store(m.group(2)):
                    out = git("ls-tree", head, "--", m.group(2)).split()
                    f["inputs_repo_ok"][m.group(2)] = bool(out) and out[1] == "blob"
        if any(p.startswith("data/") for p in f["changed_files"]):
            f["main_labels"] = labels_at(base_ref)
            b = show(base_ref, BASELINE)
            if b is None:
                f["uninspectable"].append(f"{BASELINE} is not on {base_ref}")
            else:
                f["baseline_labels"] = [ln for ln in b.splitlines() if ln.strip() and not ln.startswith("#")]
            f["audit_texts"] = {p: show(base_ref, p) for p in
                                filter(AUDIT_PATH.match, git("ls-tree", "-r", "-z", "--name-only", base_ref, "--", "tasks/").split("\0"))}
    except InspectionError as e:
        f["uninspectable"].append(str(e))
    return f


def post_check(head_sha, rc, text, name="pr-rules", conclusion=None):
    """Publish the result as a check run on the PR head (GitHub Actions app, via GITHUB_REPOSITORY)."""
    repo = os.environ["GITHUB_REPOSITORY"]
    conclusion = conclusion or ("success" if rc == 0 else "failure")
    payload = {"name": name, "head_sha": head_sha, "status": "completed", "conclusion": conclusion,
               "output": {"title": f"{name}: {conclusion}", "summary": "```\n" + text[-60000:] + "\n```"}}
    r = subprocess.run(["gh", "api", "-X", "POST", f"repos/{repo}/check-runs", "--input", "-"],
                       input=json.dumps(payload), capture_output=True, text=True)
    if r.returncode:
        print("could not post the pr-rules check run: " + r.stderr.strip()[:200])
    return r.returncode == 0


GATE_STATES = {"passed": "success", "not_yet": "success", "failed": "failure", "cannot_inspect": "failure"}


def publish_gate(dirpath, pr_number):
    """Post the binding-gate job's result (head, state, log files in `dirpath`) as the check run `binding-gate`.
    `not_yet` (the gate is not on main, so nothing was checked) posts success with that stated in the summary; nothing is neutral."""
    d = Path(dirpath)
    head, state = (d / "head").read_text().strip(), (d / "state").read_text().strip()
    log = (d / "log").read_text(errors="replace") if (d / "log").exists() else ""
    if state not in GATE_STATES or not re.fullmatch(r"[0-9a-f]{40}", head):
        print(f"gate result unusable: state {state!r}, head {head!r}")
        return 1
    live = gh_json("pr", "view", str(pr_number), "--json", "headRefOid")["headRefOid"]
    if live != head:
        print(f"PR head moved ({head[:8]} -> {live[:8]}): not posting a result for a stale head")
        return 0
    return 0 if post_check(head, 0, f"binding gate: {state}\n{log}", "binding-gate", GATE_STATES[state]) else 1


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
    ap.add_argument("--base", help="base ref (default origin/<the PR's base branch>)")
    ap.add_argument("--post", action="store_true", help="publish the result as the check run pr-rules on the PR head")
    ap.add_argument("--write-baseline", action="store_true")
    ap.add_argument("--publish-gate", metavar="DIR")
    a = ap.parse_args(argv)
    if a.publish_gate:
        if not a.pr:
            ap.error("--publish-gate needs --pr")
        return publish_gate(a.publish_gate, a.pr)
    if a.write_baseline:
        write_baseline(a.base or "origin/main")
        return 0
    if a.facts:
        return run(json.loads(Path(a.facts).read_text()))
    if not a.pr:
        ap.error("give --facts, --pr or --write-baseline")
    lines = []
    f = collect(a.pr, a.base)
    rc = run(f, lambda s: (lines.append(s), print(s)))
    if a.post:
        sha = (f.get("pr") or {}).get("head_sha")
        if not sha or not post_check(sha, rc, "\n".join(lines)):
            return 1
    return rc


if __name__ == "__main__":
    sys.exit(main())
