"""Controller-only evidence replay at the draw SHA, with offline, checksum-bound captures."""
import argparse
from collections import defaultdict
from functools import lru_cache
import importlib.util
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parent))
from packets import csv_rows, draw, read_draw, record_key, records_for_stage, unique
from adjudicate_fetch import quote_in_order

STORE = Path("/Volumes/johnpswan/work/GAC/polymer-atlas/atlas-store")
GATE_FILES = ("check_evidence_binding.py", "atlas.py", "matching.py", "build_echo_spine.py")
EVIDENCED = {"organizations", "ecosystem", "sites", "people", "programs"}


def pinned_gate(at):
    draw.require_ancestor(at)
    modules = [Path(name).stem for name in GATE_FILES[1:]]
    previous = {name: sys.modules.pop(name) for name in modules if name in sys.modules}
    search_path = sys.path[:]
    try:
        with tempfile.TemporaryDirectory() as tmp:
            scripts = Path(tmp) / "scripts"
            scripts.mkdir()
            for name in GATE_FILES:
                data = subprocess.check_output(["git", "show", f"{at}:scripts/{name}"], cwd=draw.ROOT)
                (scripts / name).write_bytes(data)
            spec = importlib.util.spec_from_file_location("audit12_pinned_gate", scripts / GATE_FILES[0])
            gate = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(gate)
    finally:
        sys.path[:] = search_path
        for name in modules:
            sys.modules.pop(name, None)
        sys.modules.update(previous)
    gate.ROOT = gate.TREE = draw.ROOT
    return gate


class Replay:
    def __init__(self, at, store, captures=()):
        gate = pinned_gate(at)
        self.gate, self.at, self.store = gate, at, store
        self.idx = gate.Index.load(at)
        self.archives, problems = gate.archive_index(gate.rows(at, "archive_links.csv"))
        if problems:
            raise ValueError("archive index has duplicate evidence IDs")
        self.evidence = defaultdict(list)
        all_evidence = unique(gate.rows(at, "evidence_*.csv"), lambda r: r["evidence_id"])
        for row in all_evidence.values():
            self.evidence[row["record_table"], row["record_id"]].append(row)
        self.captures = unique(captures, lambda r: r["evidence_id"])
        if self.captures.keys() - all_evidence.keys():
            raise ValueError("capture manifest contains unknown evidence IDs")

    def read(self, path):
        return self.gate.tasks_file(self.at, path)

    @lru_cache(maxsize=64)
    def proof_bundle(self, folder):
        path = f"tasks/{folder}/BINDING_PROOF.csv"
        data = self.read(path) if folder else None
        if not data:
            return {}, "", {}
        proofs, faults = self.gate.load_proof_file(path, data)
        if faults:
            raise ValueError("malformed stored proof")
        hashes = defaultdict(list)
        for line in (self.read(f"tasks/{folder}/INPUTS.sha256") or b"").decode().splitlines():
            digest, rel = line.split("  ", 1)
            hashes[digest].append(rel)
        return proofs, self.gate.builder_family(self.read(f"tasks/{folder}/README.md")), hashes

    @lru_cache(maxsize=32)
    def read_capture(self, path, expected):
        rel = Path(path)
        if rel.is_absolute() or ".." in rel.parts or not rel.parts or rel.parts[0] not in ("raw", "provenance"):
            raise ValueError("capture path must be under raw/ or provenance/")
        root = self.store.resolve(strict=True)
        file = (root / rel).resolve(strict=True)
        if not file.is_relative_to(root / rel.parts[0]) or not file.is_file():
            raise ValueError("capture is outside the permitted store directory")
        with file.open("rb") as f:
            raw = f.read(self.gate.MAX_CAPTURE_BYTES + 1)
        if len(raw) > self.gate.MAX_CAPTURE_BYTES or draw.sha(raw) != expected:
            raise ValueError("capture size or checksum differs")
        return raw

    def capture_matches(self, ev, capture):
        source = ev["source_ref"]
        if capture == source:
            if source.startswith(("http://", "https://")):
                self.gate.capture_url(capture)
            return True
        archive = self.archives.get(ev["evidence_id"])
        m = self.gate.ARCHIVE_RE.fullmatch(capture)
        return bool(m and archive and source.startswith(("http://", "https://"))
                    and archive["captured_at"] == f"{m[1][:4]}-{m[1][4:6]}-{m[1][6:8]}"
                    and archive["archive_ref"] == capture.replace(m[1] + "id_/", m[1] + "/", 1)
                    and self.gate.same_page(m[3], source))

    def row(self, ev):
        gate = self.gate
        verdict, reason, _ = gate.judge(ev, self.idx)
        quote = ev["claim_detail"].partition("quote:")[2].strip()
        if not quote:
            return "UNRESOLVED", "no_verbatim_quote"
        eid = ev["evidence_id"]
        try:
            proofs, builder, hashes = self.proof_bundle(gate.label_folder(ev["created_by"]))
            proof = proofs.get(eid, (None, None))[1]
            capture = self.captures.get(eid)
            if proof and verdict == "READ_REQUIRED" and reason == "mechanics_clear":
                checksum = proof["capture_sha256"]
                if not self.capture_matches(ev, proof["capture"]):
                    return "UNRESOLVED", "proof_citation_differs"
                observed = gate.proof_date(ev["observed_date"])
                gate.proof_capture(proof, ev, self.idx, self.idx, self.archives.get(eid), observed)
                if len(hashes.get(checksum, ())) != 1:
                    return "UNRESOLVED", "proof_capture_path_unavailable"
                raw = self.read_capture(hashes[checksum][0], checksum)
                page = gate.capture_text(raw)
            elif capture:
                if not self.capture_matches(ev, capture["capture_ref"]):
                    return "UNRESOLVED", "capture_citation_differs"
                raw = self.read_capture(capture["path"], capture["sha256"])
                page = gate.capture_text(raw) if capture["format"] == "html" else raw.decode("utf-8")
            else:
                return "UNRESOLVED", "capture_unavailable"
        except (OSError, ValueError):
            return "UNRESOLVED", "capture_or_proof_unreadable"

        if not page.strip():
            return "UNRESOLVED", "capture_text_empty"
        if not quote_in_order(page, quote):
            return "FIELD_ERROR", "quote_absent_from_capture"
        if verdict == "FAIL":
            return "FIELD_ERROR", reason
        if verdict == "PASS":
            return "PASS", "binding_and_quote_replayed"
        if verdict == "READ_REQUIRED" and reason == "mechanics_clear" and proof:
            try:
                problem = gate.proof_problem(proof, ev, self.idx, self.idx, self.archives.get(eid),
                                             observed, builder, lambda _: raw)
            except (KeyError, ValueError):
                problem = True
            if not problem:
                return "PASS", "web_proof_replayed"
            return "UNRESOLVED", "web_proof_did_not_replay"
        return "UNRESOLVED", reason

    def records(self, keys):
        result = []
        for table, rid in keys:
            rows = []
            for ev in self.evidence[table, rid]:
                status, reason = self.row(ev)
                rows.append(dict(evidence_id=ev["evidence_id"], status=status, reason=reason))
            statuses = {r["status"] for r in rows}
            if "FIELD_ERROR" in statuses:
                grade = "FIELD_ERROR"
            elif "UNRESOLVED" in statuses or not rows and table in EVIDENCED:
                grade = "UNRESOLVED"
            else:
                grade = "PASS" if rows else "NO_EVIDENCE_ROWS"
            result.append(dict(table=table, record_id=rid, status=grade, evidence=rows))
        return result


def capture_rows(path):
    rows = csv_rows(path.read_text())
    fields = {"evidence_id", "capture_ref", "sha256", "path", "format"}
    for r in rows:
        if (r.keys() != fields or r["format"] not in ("html", "text")
                or not re.fullmatch(r"[a-f0-9]{64}", r["sha256"])):
            raise ValueError("malformed capture manifest")
    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--draw", required=True, type=Path)
    parser.add_argument("--store", type=Path, default=STORE)
    parser.add_argument("--captures", type=Path)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--extend", nargs="+", choices=draw.STRATA, default=[])
    args = parser.parse_args()
    try:
        receipt, _, sample, _ = read_draw(args.draw)
        rows = list(records_for_stage(sample, args.extend))
        if args.extend and set(args.extend) != {r["stratum"] for r in rows}:
            raise ValueError("each requested extension must have stage-2 rows")
        replay = Replay(receipt["at"], args.store, capture_rows(args.captures) if args.captures else ())
        report = replay.records(map(record_key, rows))
        draw.write_private(args.out, json.dumps(dict(at=receipt["at"], records=report), indent=2) + "\n")
    except (OSError, ValueError, KeyError, subprocess.CalledProcessError) as exc:
        parser.exit(1, f"evidence replay refused ({type(exc).__name__})\n")
    print(f"Wrote replay results for {len(report)} sampled records")


if __name__ == "__main__":
    main()
