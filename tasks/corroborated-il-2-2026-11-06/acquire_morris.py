"""Reacquire the required Morris witness; fail closed if reviewed content changes."""
import hashlib,importlib.util,json,re,subprocess
from pathlib import Path
H=Path(__file__).resolve().parent;ROOT=H.parents[1]
spec=importlib.util.spec_from_file_location('house_fetch',ROOT/'tasks/markets-certs-tier1-2026-11-06/fetch.py')
house=importlib.util.module_from_spec(spec);spec.loader.exec_module(house)
def normalize(text):
 # The plant page displays a live local clock; only clock text and whitespace are non-evidentiary.
 return ' '.join(re.sub(r'\b\d{1,2}:\d{2}(?:am|pm)\b','[local time]',text).split())
def main():
 receipt=json.loads((H/'morris_rawcheck.json').read_text())
 p=subprocess.run(['curl','-fLsS','--max-time','35','--max-filesize','12000000','-A','Mozilla/5.0 (Atlas evidence re-verification)',receipt['url']],capture_output=True,check=True)
 page=house.Page();page.feed(p.stdout.decode('utf-8',errors='strict'));text=normalize(' '.join(page.parts))
 assert hashlib.sha256(text.encode()).hexdigest()==receipt['page_sha256'],'Morris page content changed; review and re-freeze witness, never bypass hash'
 assert all(q in text for q in [receipt['quote'],'8805 N. Tabler Road','Morris, IL 60450']),'plant quote/address binding absent'
 target=ROOT/receipt['page'];target.parent.mkdir(parents=True,exist_ok=True);target.write_text(text,encoding='utf-8')
 print('PASS acquired Morris quote/address and reviewed normalized SHA256',receipt['page_sha256'])
if __name__=='__main__':main()
