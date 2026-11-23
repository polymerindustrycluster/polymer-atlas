#!/usr/bin/env python3
"""Nightly watch: a scheduled check on `main` that needs no agent session awake (tasks/nightly-watch-2026-11-22/).

On 2026-11-21 and 22 one harness merged 28 pull requests, 34,094 evidence rows and 6,837 registry links, most before
the required check finished, and it was noticed only because the owner asked. This script looks at a window on
`main` (default: the last 24 hours) and exits non-zero when any of these holds:

  a  more than MAX_EVIDENCE_ROWS evidence rows added under one created_by label or by one pull request, or more than
     MAX_LINKS registry links added by one pull request (registry_links.csv has no created_by column)
  b  a merged pull request that changed data/ with fewer than MIN_REVIEW_RECORDS comments starting "**Review record**"
     posted before the merge
  c  a pull request merged without a successful `validate` check on its head that had finished by the merge time
     (a PR merged into a merge-train branch is exempt: the train PR that reaches main is judged instead)
  d  the latest completed `validate` run on main is not success
  e  MIN_DATA_PRS or more data/ pull requests merged while none of the three PIC-18 unknown counts fell
  f  an evidence row added in the window whose created_by label is new (not in label_baseline.txt) and names no
     folder under tasks/ (260 older labels never had one; the baseline is frozen, see the task README)
  g  keyed rows removed from data/ (or tracked files elsewhere) with no REMOVALS.csv entry (scripts/check_row_loss.py)

Rows are counted per first-parent commit (so a batch merged and then reverted the same day still counts), never as a
net window diff. Anything it could not inspect (a failed gh call, an unreadable file, a shallow clone) is an error
and also exits non-zero. It always prints what it inspected. Exit code: 0 clean, 1 findings, 2 inspection errors only.

Usage (run from a full clone; the gh CLI needs GH_TOKEN, which Actions sets):
  python3 scripts/nightly_watch.py                                  # last 24 hours on origin/main (or main)
  python3 scripts/nightly_watch.py --since 2026-11-21T06:17Z --until 2026-11-22T06:17Z   # one night, for a backfill
  python3 scripts/nightly_watch.py --since <ref>                    # from a commit, to now
  python3 scripts/nightly_watch.py --facts FILE.json                # offline: judge a saved facts file
  python3 scripts/nightly_watch.py --save-facts FILE.json           # also write the facts it collected (counts only)
"""
import argparse, csv, io, json, os, re, subprocess, sys
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import check_row_loss as rowloss
from regions import PIC18

ROOT = HERE.parent
MAX_EVIDENCE_ROWS = 1000  # a: per created_by label, and per pull request
MAX_LINKS = 1000          # a: registry links per pull request
MIN_REVIEW_RECORDS = 2    # b
MIN_DATA_PRS = 3          # e
REVIEW_PREFIX = "**Review record**"
VALIDATE = "validate"     # the check-run (job) name and the workflow file validate.yml
MIN_FOLDER_LEN = 6        # f: shorter folder names are too generic to name a label
BASELINE_FILE = ROOT / "tasks" / "nightly-watch-2026-11-22" / "label_baseline.txt"  # f: labels grandfathered at ship


def parse_time(s):
    return datetime.fromisoformat(s.replace("Z", "+00:00")).astimezone(timezone.utc)


def iso(dt):
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


# ---------------------------------------------------------------- git and gh (collection)

def git(*args, check=True):
    r = subprocess.run(["git", "-C", str(ROOT), *args], capture_output=True, text=True)
    if check and r.returncode:
        raise RuntimeError(f"git {' '.join(args[:3])}: {r.stderr.strip()[:200]}")
    return r.stdout


def gh(*args):
    r = subprocess.run(["gh", *args], capture_output=True, text=True, timeout=300)
    if r.returncode:
        raise RuntimeError(f"gh {' '.join(args[:3])}: {r.stderr.strip()[:200]}")
    return r.stdout


def blob(ref, path):
    r = subprocess.run(["git", "-C", str(ROOT), "show", f"{ref}:{path}"], capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else ""  # absent at that ref: a new (or deleted) file


def csv_rows(text):
    return list(csv.DictReader(io.StringIO(text)))


def unknown_counts(ref):
    """PIC-18 org-grain unknown counts at a ref: S/harness/pic18_unknown.py, same definition as site-prospects verify.py."""
    names = [n for n in git("ls-tree", "--name-only", ref, "data/").split() if n.endswith(".csv")]
    rows = lambda pfx: [r for n in names if n.split("/")[-1].startswith(pfx) for r in csv_rows(blob(ref, n))]
    orgs = {o["org_id"]: o for o in rows("organizations_")}
    eco = {o["org_id"]: o for o in rows("ecosystem.csv")}
    toks = lambda v: {t.strip() for t in (v or "").split(";") if t.strip() and t.strip() != "unknown"}
    gt = defaultdict(list)
    for s in rows("sites_"):
        if (s["state"] == "OH" and s["county"] in PIC18 and s["operating_status"] == "active"
                and s["verification_tier"] in "ABC" and s["verification_tier"]):
            gt[s["org_id"]].append(s)
    unk = {"proc": 0, "mkt": 0, "band": 0}
    for oid, ss in gt.items():
        rec = orgs.get(oid) or eco.get(oid) or {}
        for k, (sf, of) in {"proc": ("processes", "processes"), "mkt": ("markets_served", "markets_served"),
                            "band": ("employee_band_site", "employee_band_ohio")}.items():
            t = set().union(*(toks(s[sf]) for s in ss)) or toks(rec.get(of))
            unk[k] += not t
    return {"n": len(gt), **unk}


def labels_at(ref):
    """Distinct evidence created_by labels at a ref that name no tasks/ folder at that ref (the grandfathered set)."""
    names = [n for n in git("ls-tree", "--name-only", ref, "data/").split() if re.match(r"data/evidence.*\.csv$", n)]
    folders = [n.split("/")[-1] for n in git("ls-tree", "--name-only", ref, "tasks/").split("\n") if n]
    labels = {r["created_by"] for n in names for r in csv_rows(blob(ref, n))}
    return sorted(l for l in labels if l and "\n" not in l and not label_names_a_folder(l, folders))


def commit_changes(sha, trees):
    """Evidence rows and registry links a first-parent commit added, plus keyed rows it removed undeclared."""
    parent = sha + "^1"
    changed = [p for p in git("diff", "--name-only", "-z", parent, sha).split("\0") if p]
    data = [p for p in changed if p.startswith("data/")]
    ev_old, ev_new, links = {}, {}, 0
    for p in (p for p in data if re.match(r"data/evidence.*\.csv$", p)):
        ev_old.update({r["evidence_id"]: r for r in csv_rows(blob(parent, p))})
        ev_new.update({r["evidence_id"]: r for r in csv_rows(blob(sha, p))})
    added = Counter(r["created_by"] for k, r in ev_new.items() if k not in ev_old)
    if "data/registry_links.csv" in data:
        key = lambda r: tuple(r.get(c, "") for c in rowloss.COMPOSITE["registry_links"])
        links = len({key(r) for r in csv_rows(blob(sha, "data/registry_links.csv"))}
                    - {key(r) for r in csv_rows(blob(parent, "data/registry_links.csv"))})
    removed = {}
    allowed = {(t, k) for _, t, k in rowloss.declared_removals(sha) - rowloss.declared_removals(parent)}
    if data:
        for t, ks in rowloss.removed_keys(trees(parent), trees(sha), allowed).items():
            removed[t] = {"n": len(ks), "e.g.": ks[:3]}
    gone = rowloss.removed_files(rowloss.tracked_files(parent), rowloss.tracked_files(sha), allowed)
    if gone:
        removed["file"] = {"n": len(gone), "e.g.": gone[:3]}
    return {"data_files": len(data), "evidence_added": dict(added), "links_added": links, "removed": removed}


def collect(ref, since, until, repo, errors):
    """Build the facts dict for the window (since, until] on ref. Failures are appended to errors, never swallowed."""
    facts = {"ref": ref, "since": iso(since), "until": iso(until), "errors": errors, "commits": [], "prs": []}
    if git("rev-parse", "--is-shallow-repository").strip() == "true":
        errors.append("shallow clone: history is incomplete (use fetch-depth: 0)")
        return facts
    before = lambda t: git("rev-list", "-1", "--first-parent", f"--before={iso(t)}", ref).strip()
    base, head = before(since), before(until)
    if not base or not head:
        errors.append(f"no commit on {ref} before {iso(since if not base else until)}: window start not resolvable")
        return facts
    facts.update(base=base[:10], head=head[:10])
    shas = git("rev-list", "--first-parent", "--reverse", f"{base}..{head}").split()
    tree_cache = {}
    def trees(sha):
        if sha not in tree_cache:
            tree_cache.clear()  # consecutive first-parent commits share a tree; keep only the last
            tree_cache[sha] = rowloss.read_tree(sha)
        return tree_cache[sha]
    for sha in shas:
        try:
            c = {"sha": sha[:10], "date": git("show", "-s", "--format=%cI", sha).strip(),
                 "subject": git("show", "-s", "--format=%s", sha).strip()[:90], "pr": None}
            c.update(commit_changes(sha, trees))
            facts["commits"].append(c)
        except Exception as e:  # keep going: one unreadable commit must not hide the others
            errors.append(f"commit {sha[:10]}: {e}")
    try:
        names = [n for n in git("ls-tree", "--name-only", head, "tasks/").split("\n") if n]
        facts["task_folders"] = [n.split("/")[-1] for n in names]
        baseline = set(BASELINE_FILE.read_text().splitlines())
        added = {l for c in facts["commits"] for l in c["evidence_added"]}
        facts["labels_without_provenance"] = sorted(l for l in added if l not in baseline and not label_names_a_folder(l, facts["task_folders"]))
        facts["task_folders_read"] = len(facts.pop("task_folders"))
        facts["unknown"] = {"before": unknown_counts(base), "after": unknown_counts(head)}
    except Exception as e:
        errors.append(f"tasks/ folders, label baseline or PIC-18 unknown counts: {e}")
    try:
        collect_github(facts, shas, since, until, repo)
    except Exception as e:
        errors.append(f"GitHub: {e}")
    return facts


def collect_github(facts, shas, since, until, repo):
    pad = timedelta(days=1)
    search = f"merged:{(since - pad).date()}..{(until + pad).date()}"
    prs = json.loads(gh("pr", "list", "--repo", repo, "--state", "merged", "--base", "main", "--search", search,
                        "--limit", "1000", "--json", "number,mergedAt,mergeCommit,headRefOid,comments"))
    if len(prs) >= 1000:
        facts["errors"].append("pr list returned 1000 rows: window too large to inspect completely")
    by_merge = {p["mergeCommit"]["oid"][:10]: p for p in prs if p.get("mergeCommit")}
    sha10 = {c["sha"]: c for c in facts["commits"]}
    in_window = {s[:10] for s in git("rev-list", f"{facts['base']}..{facts['head']}").split()}
    seen = set()
    for s in sorted(in_window & by_merge.keys(), key=lambda k: by_merge[k]["mergedAt"]):
        p = by_merge[s]
        if s in sha10:
            sha10[s]["pr"] = p["number"]
            data_files = sha10[s]["data_files"]
            train = False
        else:  # merged into a merge-train branch: its rows ride on the train PR's own first-parent commit
            data_files = sum(1 for f in git("diff", "--name-only", s + "^1", s).split() if f.startswith("data/"))
            train = True
        merged = parse_time(p["mergedAt"])
        records = sum(1 for c in p["comments"]
                      if c["body"].lstrip().startswith(REVIEW_PREFIX) and parse_time(c["createdAt"]) < merged)
        runs = [json.loads(line) for line in gh(
            "api", "--paginate", f"repos/{repo}/commits/{p['headRefOid']}/check-runs?filter=all&per_page=100",
            "-q", ".check_runs[] | select(.name==\"" + VALIDATE + "\") | {status,conclusion,started_at,completed_at}"
        ).splitlines() if line.strip()]
        started = [r for r in runs if r["started_at"] and parse_time(r["started_at"]) < merged]
        later = [r for r in runs if r not in started and r["started_at"]]
        last = (max(started, key=lambda r: r["started_at"]) if started
                else dict(min(later, key=lambda r: r["started_at"]), late=True) if later else None)
        facts["prs"].append({"number": p["number"], "merged_at": p["mergedAt"], "merge_sha": s, "train_member": train,
                             "head_sha": p["headRefOid"][:10], "data_files": data_files,
                             "review_records": records, "validate": last})
        seen.add(p["number"])
    for c in facts["commits"]:  # b and c cannot be judged for a commit no PR explains (a direct push, or a missed search)
        if not c["pr"]:
            facts["errors"].append(f"commit {c['sha']} on {facts['ref']} is the merge commit of no merged PR "
                                   f"(a direct push, or the PR search missed it): b and c not judged for it")
    for p in prs:  # a PR merged inside the window that no commit of the window explains cannot be judged
        if p["number"] not in seen and since < parse_time(p["mergedAt"]) <= until:
            facts["errors"].append(f"PR #{p['number']} merged in the window but its merge commit is not in the "
                                   f"history of {facts['ref']} between {facts['base']} and {facts['head']}")
    runs = gh("api", f"repos/{repo}/actions/workflows/{VALIDATE}.yml/runs?branch=main&event=push&status=completed"
                     f"&created=<={iso(until)}&per_page=1", "-q", ".workflow_runs[0] // empty | "
              "{conclusion, created_at, head_sha: .head_sha[:10]}").strip()
    if runs:
        facts["main_validate"] = json.loads(runs)
    else:
        facts["errors"].append(f"no completed {VALIDATE} run on main found at or before {iso(until)}")


# ---------------------------------------------------------------- the judgement (pure: facts in, findings out)

def label_names_a_folder(label, folders):
    """A created_by label names a tasks/ folder when a folder name (>= MIN_FOLDER_LEN chars) is inside it."""
    return any(len(f) >= MIN_FOLDER_LEN and f in label for f in folders)


def analyze(facts):
    """Return (findings, errors). Every finding is one printable line with its numbers."""
    findings, errors = [], list(facts.get("errors", []))
    commits, prs = facts["commits"], facts["prs"]
    data_prs = [p for p in prs if p["data_files"]]
    data_prs_e = [p for p in data_prs if not p["train_member"]]  # the train PR stands for its members

    per_label = Counter()
    for c in commits:
        per_label.update(c["evidence_added"])
    for label, n in sorted(per_label.items(), key=lambda kv: -kv[1]):
        if n > MAX_EVIDENCE_ROWS:
            findings.append(f"[a] created_by '{label}': {n:,} evidence rows added (limit {MAX_EVIDENCE_ROWS:,})")
    for c in commits:
        n, links = sum(c["evidence_added"].values()), c["links_added"]
        who = f"PR #{c['pr']}" if c["pr"] else f"commit {c['sha']} (no PR)"
        if n > MAX_EVIDENCE_ROWS:
            findings.append(f"[a] {who}: {n:,} evidence rows added (limit {MAX_EVIDENCE_ROWS:,})")
        if links > MAX_LINKS:
            findings.append(f"[a] {who}: {links:,} registry links added (limit {MAX_LINKS:,})")

    for p in data_prs:
        if p["review_records"] < MIN_REVIEW_RECORDS:
            findings.append(f"[b] PR #{p['number']} changed data/ and has {p['review_records']} "
                            f"'{REVIEW_PREFIX}' comment(s) before merge (need {MIN_REVIEW_RECORDS})")

    for p in prs:
        if p["train_member"]:  # merged into a train branch; the train PR's own validate is judged when it reaches main
            continue
        v = p["validate"]
        if v is None:
            findings.append(f"[c] PR #{p['number']} merged {p['merged_at']}; its head {p['head_sha']} has no {VALIDATE} check at all")
        elif v.get("late"):
            findings.append(f"[c] PR #{p['number']} merged {p['merged_at']} before any {VALIDATE} check started on its head "
                            f"(first started {v['started_at']}, {v['conclusion'] or v['status']})")
        elif not v["completed_at"] or v["status"] != "completed" or parse_time(v["completed_at"]) > parse_time(p["merged_at"]):
            findings.append(f"[c] PR #{p['number']} merged {p['merged_at']} before its {VALIDATE} check finished "
                            f"(status {v['status']}, completed {v['completed_at']})")
        elif v["conclusion"] != "success":
            findings.append(f"[c] PR #{p['number']} merged with {VALIDATE} = {v['conclusion']} on its head {p['head_sha']}")

    mv = facts.get("main_validate")
    if mv and mv["conclusion"] != "success":
        findings.append(f"[d] latest completed {VALIDATE} run on main ({mv['head_sha']}, {mv['created_at']}) is {mv['conclusion']}")

    unk = facts.get("unknown")
    if unk and len(data_prs_e) >= MIN_DATA_PRS:
        b, a = unk["before"], unk["after"]
        if all(a[k] >= b[k] for k in ("proc", "mkt", "band")):
            findings.append(f"[e] {len(data_prs_e)} data/ PRs merged and no PIC-18 unknown count fell: process {b['proc']}->{a['proc']}, "
                            f"market {b['mkt']}->{a['mkt']}, size {b['band']}->{a['band']} (of {b['n']}->{a['n']} org rows)")

    if "labels_without_provenance" not in facts:
        errors.append("f not judged: labels_without_provenance missing from the facts")
    else:
        for label, n in sorted(per_label.items(), key=lambda kv: -kv[1]):
            if label in facts["labels_without_provenance"]:
                findings.append(f"[f] created_by '{label}': {n:,} evidence row(s) added; new label, and no tasks/ folder name appears in it")

    for c in commits:
        for t, r in sorted(c["removed"].items()):
            who = f"PR #{c['pr']}" if c["pr"] else f"commit {c['sha']} (no PR)"
            findings.append(f"[g] {who}: {r['n']:,} {t} key(s) removed without a REMOVALS.csv entry, e.g. {', '.join(r['e.g.'])}")
    return findings, errors


def inspected(facts):
    cs, prs = facts["commits"], facts["prs"]
    ev, links = sum(sum(c["evidence_added"].values()) for c in cs), sum(c["links_added"] for c in cs)
    data_c = sum(1 for c in cs if c["data_files"])
    lines = [f"window {facts['since']} .. {facts['until']} on {facts['ref']} (base {facts.get('base')}, head {facts.get('head')})",
             f"commits: {len(cs)} first-parent ({data_c} touching data/, {sum(1 for c in cs if not c['pr'])} with no PR)",
             "pull requests: " + (", ".join(f"#{p['number']}" + ("t" if p["train_member"] else "") for p in prs) or "none")
             + (" (t = merged into a merge train)" if any(p["train_member"] for p in prs) else ""),
             f"rows added: {ev:,} evidence ({len(Counter(l for c in cs for l in c['evidence_added']))} created_by labels), {links:,} registry links",
             f"tasks/ folders read: {facts.get('task_folders_read', 0)}; labels without provenance: {len(facts.get('labels_without_provenance', []))}"]
    if facts.get("unknown"):
        b, a = facts["unknown"]["before"], facts["unknown"]["after"]
        lines.append(f"PIC-18 unknown counts (process/market/size): {b['proc']}/{b['mkt']}/{b['band']} -> {a['proc']}/{a['mkt']}/{a['band']}")
    mv = facts.get("main_validate")
    lines.append(f"latest completed {VALIDATE} run on main: {mv['conclusion'] if mv else 'not read'}")
    return lines


def report(facts):
    findings, errors = analyze(facts)
    out = ["NIGHTLY WATCH — inspected:"] + ["  " + l for l in inspected(facts)]
    out += [f"FINDING {f}" for f in findings] + [f"ERROR could not inspect: {e}" for e in errors]
    out.append("RESULT: " + ("FAIL — findings above" if findings else "FAIL — inspection incomplete" if errors else "PASS — no finding in the window"))
    return "\n".join(out), (1 if findings else 2 if errors else 0)


def resolve_since(s, ref, until):
    if re.fullmatch(r"\d+(\.\d+)?", s):
        return until - timedelta(hours=float(s))
    try:
        return parse_time(s if "T" in s else s + "T00:00:00Z")
    except ValueError:
        return parse_time(git("show", "-s", "--format=%cI", s + "^{commit}").strip())  # a ref: from that commit's date


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--since", default="24", help="hours back from --until, an ISO date/time, or a git ref (default 24)")
    ap.add_argument("--until", help="ISO date/time (default now)")
    ap.add_argument("--ref", help="branch to watch (default origin/main, else main)")
    ap.add_argument("--repo", default=os.environ.get("GITHUB_REPOSITORY"), help="owner/name (default $GITHUB_REPOSITORY, else gh)")
    ap.add_argument("--print-label-baseline", metavar="REF", help="print the grandfathered label list at REF and exit")
    ap.add_argument("--facts", help="judge a saved facts JSON file instead of collecting")
    ap.add_argument("--save-facts", help="write the collected facts (counts only) to this JSON file")
    ap.add_argument("--report-file", help="also write the report text here (the workflow files an issue from it)")
    a = ap.parse_args()
    if a.print_label_baseline:
        print("\n".join(labels_at(a.print_label_baseline)))
        return 0
    if a.facts:
        facts = json.loads(Path(a.facts).read_text())
    else:
        errors = []
        try:
            ref = a.ref or ("origin/main" if git("rev-parse", "--verify", "-q", "origin/main", check=False).strip() else "main")
            until = parse_time(a.until if "T" in (a.until or "T") else a.until + "T00:00:00Z") if a.until else datetime.now(timezone.utc)
            since = resolve_since(a.since, ref, until)
            repo = a.repo or gh("repo", "view", "--json", "nameWithOwner", "-q", ".nameWithOwner").strip()
            facts = collect(ref, since, until, repo, errors)
        except Exception as e:  # even the setup failing must produce a loud, non-zero report
            facts = {"ref": a.ref, "since": a.since, "until": a.until or "now", "errors": errors + [f"setup: {e}"], "commits": [], "prs": []}
    if a.save_facts:
        Path(a.save_facts).write_text(json.dumps(facts, indent=1, sort_keys=True) + "\n")
    text, code = report(facts)
    print(text)
    if a.report_file:
        Path(a.report_file).write_text(text + "\n")
    return code


if __name__ == "__main__":
    sys.exit(main())
