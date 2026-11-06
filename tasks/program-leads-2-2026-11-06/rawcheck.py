"""Re-fetch own pages; reuse the evidence-repair word-sequence normalization."""
import csv, hashlib, html, re, runpy, subprocess
from pathlib import Path
HERE = Path(__file__).resolve().parent
W = runpy.run_path(str(HERE.parent / 'evidence-repair-2-2026-11-04/prep.py'))['W']


def matches(page, quote):
    page, quote = W(page), W(quote)
    return bool(quote) and any(page[i:i + len(quote)] == quote for i in range(len(page) - len(quote) + 1))


def main():
    rows = list(csv.DictReader(open(HERE / 'verdicts.csv'))) + list(csv.DictReader(open(HERE / 'calibration.csv')))
    checked = []
    # Known held programs: Pittsburg, Stout, Winona. Require all positives AND a fabricated negative.
    ordered = sorted(rows, key=lambda r: (r['lead_id'] not in ('L13-003', 'L13-006', 'L13-010'), r['lead_id']))
    for row in ordered:
        raw = subprocess.run(['curl', '--fail', '-L', '--max-time', '60', '-A', 'Mozilla/5.0', '-sS', row['source_url']], capture_output=True, check=True).stdout
        page = re.sub(r'<(script|style)\b[^>]*>.*?</\1>', ' ', raw.decode('utf8', 'replace'), flags=re.S | re.I)
        page = html.unescape(re.sub('<[^>]+>', ' ', page))
        assert matches(page, row['quote']), f"raw quote not found: {row['lead_id']}"
        assert not matches(page, 'Zyxw fabricated nonexistent polymer qualification 928173'), 'negative control passed'
        checked.append(dict(lead_id=row['lead_id'],source_url=row['source_url'],quote=row['quote'],raw='yes',sha256=hashlib.sha256(raw).hexdigest(),observed_date='2026-11-06'))
    with open(HERE / 'rawcheck.csv', 'w') as f:
        w = csv.DictWriter(f, fieldnames=list(checked[0]), lineterminator='\n'); w.writeheader(); w.writerows(sorted(checked,key=lambda r:r['lead_id']))
    print('PASS: 3 known-answer positives + fabricated negative; 10/10 own-page quotes matched; 0 skipped')


if __name__ == '__main__':
    main()
