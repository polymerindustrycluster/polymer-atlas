"""FTZ production-authority sample -> final verdicts. The OFIS database carries company names only (no address), so there is no establishment to
verify: a company whose exact normalized name is a held legal/trade name is DUPLICATE_OF that organization (organization grain); every other
company is STILL_UNCERTAIN with the settling fact. No own-site fetch campaign is run (fetches=0): without a street there is nothing to verify."""
import csv,sys,datetime
from pathlib import Path
HERE=Path(__file__).resolve().parent;sys.path.insert(0,str(HERE.parent));import common
def main():
 rows=list(csv.DictReader(open(HERE/'sample_pre.csv')));out=[];today=datetime.date.today().isoformat()
 for r in rows:
  names=[x for x in r['name_hits'].split(';') if x]
  if names:verdict,dup,reason='DUPLICATE_OF',names[0],f"exact normalized name is a held organization ({len(names)} held record(s)); organization grain only, FTZ authority is an approval dated {r['latest_approval']}, not current production"
  else:verdict,dup,reason='STILL_UNCERTAIN','',"no held organization with this exact name; settling fact: production-site address (OFIS zone/site list or the docketing Federal Register notice) plus own-site statement of a plastics/rubber product; an FTZ approval is not evidence of current production"
  out.append(dict(r,verdict=verdict,duplicate_of=dup,verified_new=0,verify_fetches=0,verify_date='',reason=reason,source='ITA OFIS FTZ Production Database (ofis.trade.gov/ManufacturingDB)'))
 common.write_csv(HERE/'sample.csv',out)
if __name__=='__main__':main()
