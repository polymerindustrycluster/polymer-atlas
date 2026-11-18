"""Fresh primary-source reads of large public files for blind audit 11 phase 3: the SBA PPP rows behind the seven sampled band
record changes, and the OSHA ITA 300A rows behind the three sampled tier changes.
Streams each file once, hashes the whole file, and keeps only the header plus the lines naming a sampled loan, borrower or
establishment. The extract is stored hash-named in the persist dir; the receipt records the full-file sha256 and size, so the
extract can be tied to the exact release the PR cites (#348's source_manifest.json for PPP).
Run: python3 stream_extract.py ppp|osha"""
import hashlib, json, re, subprocess, sys, tempfile
from datetime import datetime, timezone
import adjudicate_fetch as A

SBA = 'https://data.sba.gov/sites/default/files/distribution/SBA-OCA-2022-07-001/'
JOBS = {
    'ppp': ([SBA + 'public_150k_plus_240930.csv', SBA + 'public_up_to_150k_9_240930.csv'],
            rb'8191017006|2464008510|6217178505|3091617205|6820187702|6102237002|4057067109|SIMPLAY3|PACE CONVERTING|SUPERIOR MOLD|BEACON GASKET|CERTON TECH|PREMERE|SPECIALTY HOSE'),
    'osha': (['https://www.osha.gov/sites/default/largefiles/ITA_300A_Summary_Data_2025_through_08-31-2026.csv'],
             rb'(?<!\d)(?:818456|1258989|519774)(?!\d)|ALTTRAN|FABOHIO|DRECO'),
}


def extract(url, keys):
    KEYS = re.compile(keys, re.I)
    with tempfile.NamedTemporaryFile() as hdr:
        p = subprocess.Popen(['curl', '-sSL', '--max-time', '1200', '-A', A.UA, '-D', hdr.name, url], stdout=subprocess.PIPE)
        h, n, keep, first, buf = hashlib.sha256(), 0, [], None, b''
        for chunk in iter(lambda: p.stdout.read(1 << 20), b''):
            h.update(chunk)
            n += len(chunk)
            buf += chunk
            *lines, buf = buf.split(b'\n')
            for ln in lines:
                if first is None:
                    first = ln
                elif KEYS.search(ln):
                    keep.append(ln)
        if buf:
            first = first or buf
            keep += [buf] if KEYS.search(buf) else []
        p.wait()
        status = int((re.findall(rb'HTTP/\S+ (\d{3})', open(hdr.name, 'rb').read()) or [b'0'])[-1])
    body = b'\n'.join([first] + keep) + b'\n'
    sha = hashlib.sha256(body).hexdigest()
    (A.RAW / f'{sha}.bin').write_bytes(body)
    rec = dict(url=url, via='stream-extract', http_status=status, bytes=len(body), sha256=sha, file_bytes=n, file_sha256=h.hexdigest(),
               fetched_at=datetime.now(timezone.utc).isoformat(timespec='seconds'))
    with (A.H / 'adjudication_receipts.jsonl').open('a') as f:
        f.write(json.dumps(rec) + '\n')
    return rec


if __name__ == '__main__':
    A.RAW.mkdir(parents=True, exist_ok=True)
    urls, keys = JOBS[sys.argv[1]]
    for u in urls:
        r = extract(u, keys)
        print(u.rsplit('/', 1)[1], r['http_status'], r['file_bytes'], r['file_sha256'], 'kept', r['bytes'], 'bytes')
