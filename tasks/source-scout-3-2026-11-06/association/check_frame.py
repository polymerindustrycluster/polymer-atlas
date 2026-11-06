"""Re-fetch the public processor frame; never collect personal-member categories."""
import csv,html,random,re,subprocess,tempfile,hashlib
from pathlib import Path
HERE=Path(__file__).parent
URL='https://www.pmahome.org/meet-our-members'

def frame(text):
 sections=re.split(r'<h3\b[^>]*>',text)
 section=next(s for s in sections if re.sub('<[^>]*>','',s.split('</h3>',1)[0]).strip()=='Processor Members')
 # A required following section makes a broken boundary fail rather than eat supplier/person rows.
 assert any('Supplier Members' in s.split('</h3>',1)[0] for s in sections)
 return [html.unescape(re.sub('<[^>]*>','',s)).strip() for s in re.findall(r'<li\b[^>]*>(.*?)</li>',section,re.S)]

def selfcheck():
 fixture='<h3>Processor Members</h3><ul><li>ABCO Subsea LLC</li><li>ACP Composites</li><li>Chemi-Flex</li></ul><h3><span>Supplier Members</span></h3><li>Excluded Supplier</li>'
 assert frame(fixture)==['ABCO Subsea LLC','ACP Composites','Chemi-Flex']
 try:frame(fixture.replace('<h3><span>Supplier Members</span></h3>',''))
 except AssertionError:pass
 else:raise AssertionError('missing boundary was silently accepted')

def main():
 selfcheck()
 with tempfile.TemporaryDirectory() as d:
  p=Path(d)/'page.html'
  code=subprocess.check_output(['curl','-LsS','--max-time','60','-A','Mozilla/5.0',URL,'-o',str(p),'-w','%{http_code}'],text=True)
  assert code=='200',f'availability failure HTTP {code}'
  text=p.read_text();names=frame(text)
  assert len(names)==len(set(names))==95,'live roster changed: investigate before replacing pinned sample'
  sample=random.Random(20261106).sample(names,20)
  committed=[r['name'] for r in csv.DictReader((HERE/'sample.csv').open())]
  assert sample==committed,'live roster/order changed; pinned sample is historical'
  print('PASS: 95 unique processor entries; independent 20-row seeded sample matches; raw SHA256',hashlib.sha256(text.encode()).hexdigest())
if __name__=='__main__':main()
