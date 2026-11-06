#!/usr/bin/env python3
"""Re-fetch the four registry identities from FRS and DOL; fail on incomplete/mismatched yield."""
import csv
import io
import re
import subprocess
import tempfile
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
FIELDS = {'record_name':'FacilityName','street':'LocationAddress','city':'CityName','state':'StateAbbr','zip':'ZipCode'}

def main():
    expected = list(csv.DictReader((HERE/'registry_sources.csv').open()))
    assert len(expected) == 4 and len({(r['registry'],r['registry_id']) for r in expected}) == 4
    confirmed = set()
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        for i, row in enumerate(expected):
            raw = tmp/f'{i}.raw'
            subprocess.run(['curl','-fL','--max-time','90','-A','Mozilla/5.0','-sS',row['source_ref'],'-o',str(raw)],check=True)
            if row['registry'] == 'FRS':
                records=ET.fromstring(raw.read_bytes()).findall('FRSFacility')
                assert len(records)==1 and records[0].findtext('RegistryId')==row['registry_id'], 'FRS ID/yield mismatch'
                for col, xml in FIELDS.items(): assert records[0].findtext(xml)==row[col], (row['registry_id'],col)
                assert records[0].findtext('RegistryId')!='999999999999', 'negative ID control'
            else:
                with zipfile.ZipFile(raw) as z:
                    members=[n for n in z.namelist() if n.lower()=='f_5500_2024_latest.csv']
                    assert len(members)==1, 'missing/duplicate DOL CSV'
                    with z.open(members[0]) as f:
                        matches=[r for r in csv.DictReader(io.TextIOWrapper(f,encoding='utf-8-sig')) if r['ACK_ID']==row['source_record_id']]
                assert len(matches)==1, 'DOL filing yield mismatch'
                filing=matches[0]
                mapping={'record_name':'SPONSOR_DFE_NAME','street':'SPONS_DFE_MAIL_US_ADDRESS1','city':'SPONS_DFE_MAIL_US_CITY','state':'SPONS_DFE_MAIL_US_STATE','zip':'SPONS_DFE_MAIL_US_ZIP','registry_id':'SPONS_DFE_EIN'}
                assert all(filing[key]==row[col] for col,key in mapping.items()), 'R11 name/street/EIN mismatch'
                assert filing['SPONSOR_DFE_NAME']=='DOVER CHEMICAL CORPORATION' and filing['SPONS_DFE_MAIL_US_ADDRESS1']=='3676 DAVIS ROAD NW'
                assert filing['SPONS_DFE_EIN']!='000000000', 'negative EIN control'
            confirmed.add((row['registry'],row['registry_id']))
            print('SOURCE PASS',row['registry'],row['registry_id'],row['record_name'],row['street'])
        cro=tmp/'cro.pdf'
        subprocess.run(['curl','-fL','--max-time','60','-A','Mozilla/5.0','-sS','https://dam.assets.ohio.gov/image/upload/epa.ohio.gov/Portals/30/hazwaste/Historical_list_Facilities_CRO.pdf','-o',str(cro)],check=True)
        subprocess.run(['pdftotext','-layout',str(cro),str(cro.with_suffix('.txt'))],check=True)
        text=cro.with_suffix('.txt').read_text()
        block=' '.join(text[text.index('QUEST AUTOMOTIVE PRODUCTS'):].split('SIMON DUPLEX')[0].split())
        assert all(x in block for x in ['CATALYST','SYSTEMS','2557','2290 ZIMMERMAN RD SE','GNADENHUTTEN, OH 44629','OHD020626800']), 'joint facility name/address not corroborated'
    assert confirmed=={(r['registry'],r['registry_id']) for r in expected}
    print('PASS4/4 source-system identities;3 hand-known FRS records plus1 exact-name/street EIN filing; joint-name corroboration; negative ID controls')

if __name__=='__main__':main()
