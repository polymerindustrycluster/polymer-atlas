#!/usr/bin/env python3
"""Different-family reading of each capture (the binding gate's per-row proof). Sends the held name, the claimed name, the quote and the
capture's main text around it to another model family through council-ask; keeps the raw answer. Usage: reader.py FAMILY IN.jsonl OUT.jsonl"""
import json, subprocess, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'scripts'))
import check_evidence_binding as g  # noqa: E402

STORE = Path('/Volumes/johnswanson/work/GAC/polymer-atlas/atlas-store/provenance/site-name-repair-2026-11-26/captures').parent.parent.parent
STORE = Path('/Volumes/johnpswan/work/GAC/polymer-atlas/atlas-store/provenance/site-name-repair-2026-11-26/captures')
RULE = ("Owner rule: the Atlas site_name becomes the name the operator's own page prints at that street wherever the held name differs by "
        "more than a legal-form word (Inc, LLC, Corp, Co, Company, The) or punctuation; a legal entity, parent, predecessor, brand or division name counts as different.")


def main():
    fam, src, dst = sys.argv[1:4]; out = []
    for line in Path(src).read_text().splitlines():
        r = json.loads(line); ct = g.capture_text((STORE / f"{r['capture_sha256']}.html").read_bytes())
        a = r['offset']; ctx = ct[max(0, a - 300):a + len(r['quote']) + 200]
        prompt = (f"You are an independent reader. {RULE}\nHeld site name: {r['held']}\nProposed site name: {r['new_name']}\nPage: {r['url']}\n"
                  f"Quote (verbatim from the page's main text): {r['quote']}\nMain text around the quote: {ctx}\n"
                  "Question: does the page print the proposed name as the name of the establishment or operator at the street in the quote, and does the held name differ "
                  "from it by more than a legal-form word or punctuation? Do not browse. Answer one JSON object only: "
                  '{"verdict":"VERIFIED"|"REFUTE","printed_name_at_street":"<what the page prints>","reason":"<one sentence>"}')
        p = subprocess.run(['council-ask', fam, prompt], capture_output=True, text=True, timeout=900)
        out.append(dict(site_id=r['site_id'], family=fam, returncode=p.returncode, answer=p.stdout[-1500:], err=p.stderr[-300:]))
        print(r['site_id'], p.returncode, p.stdout[-400:].replace('\n', ' '), flush=True)
    Path(dst).write_text('\n'.join(json.dumps(x) for x in out) + '\n')


if __name__ == '__main__': main()
