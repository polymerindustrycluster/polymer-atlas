"""Copy the two locked reviewer outputs into this folder (blind audit 11 phase 3).
- verdicts_a.csv / verdicts_b.csv: LF-normalised copies (the repo CSV rule). On the 13 uei_links rows every free-text cell
  (field, correct_value, source_url, quote, note) is blanked, because reviewer A's cells quote SAM names and addresses and
  R-SAM (controller ruling 2026-11-17) bars them from the repo; blind_id, record_id and verdict are kept.
- receipts_a.json / receipts_b.json: byte copies (url, status, time, body hash and short notes; no SAM content).
- locks.json: the BOARD lock hash of each original and the hash of each committed copy. check.py re-applies redact() to the
  private originals when they are present and requires the committed bytes.
Run once: python3 copy_verdicts.py"""
import csv, hashlib, io, json, shutil
from pathlib import Path

H = Path(__file__).resolve().parent
PRIVATE = Path('/Users/johnswanson/.bb/thread-storage/thr_9i2c6byhcz/2026-11-06-atlas/private/audit11')
LOCKED = {'a': '0f3b1c9eb78f4620c5deb24d3023476221975f23803b4443fc972f1f75644b02',  # BOARD lock lines, 2026-11-17
          'b': '9058060d8486eae9396ed189a313552c32a984764f7f24f02fc3cde88361f0c7'}
FIELDS = ['blind_id', 'record_id', 'verdict', 'field', 'correct_value', 'source_url', 'quote', 'note']
FREE = ('field', 'correct_value', 'source_url', 'quote', 'note')
sha = lambda b: hashlib.sha256(b).hexdigest()


def redact(original: bytes) -> bytes:
    uei = {r['blind_id'] for r in csv.DictReader((H / 'sample.csv').open(newline='')) if r['change_class'] == 'uei_links'}
    rows = list(csv.DictReader(io.StringIO(original.decode('utf-8'), newline='')))
    assert len(rows) == 120 and len({r['blind_id'] for r in rows} & uei) == 13
    out = io.StringIO()
    w = csv.DictWriter(out, fieldnames=FIELDS, lineterminator='\n')
    w.writeheader()
    for r in rows:
        w.writerow({k: ('' if r['blind_id'] in uei and k in FREE else r[k]) for k in FIELDS})
    return out.getvalue().encode('utf-8')


def main():
    locks = {}
    for k in 'ab':
        src = (PRIVATE / f'out_{k}/verdicts.csv').read_bytes()
        assert sha(src) == LOCKED[k], f'{k}: original no longer matches its BOARD lock'
        red = redact(src)
        (H / f'verdicts_{k}.csv').write_bytes(red)
        shutil.copyfile(PRIVATE / f'out_{k}/receipts.json', H / f'receipts_{k}.json')
        locks[k] = dict(locked_sha256=LOCKED[k], committed_sha256=sha(red), receipts_sha256=sha((H / f'receipts_{k}.json').read_bytes()))
    (H / 'locks.json').write_text(json.dumps(locks, indent=1) + '\n')
    print(json.dumps(locks, indent=1))


if __name__ == '__main__':
    main()
