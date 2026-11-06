"""Fresh primary-page discovery cache, using the unchanged L1 fetcher."""
import concurrent.futures,json
from urllib.parse import urlsplit
from pathlib import Path
from fetch import fetch,read
H=Path(__file__).resolve().parent
SEEDS=[
'https://www.spiratex.com/careers/','https://www.spiratex.com/contact-us/','https://prismplastics.com/chesterfield/','https://prismplastics.com/port-huron/',
'https://marianinc.com/marian-chicago/','https://www.pretiumpkg.com/locations/','https://www.all-stateind.com/contact/locations/',
'https://www.trelleborg.com/en/seals/about-us/manufacturing-capabilities/streamwood-usa','https://www.trelleborg.com/fi-fi/seals/about-us/manufacturing-capabilities/streamwood-usa',
'https://careers.owenscorning.com/job/Rockford-Production-Associate-IL-61109/1446312100/',
'https://pressroom.pella.com/women-leaders-at-pella-corporation-recognized-for-excellence-in-manufacturing/',
'https://eastjordanplastics.com/blog/statement-regarding-our-south-haven-facility/','https://eastjordanplastics.com/the-sustainable-choice/',
'https://www.gilkey.com/location/chicago-ridge-il/','https://www.pregis.com/knowledge-hub/pregis-acquires-rex-performance-products/',
'https://www.pregis.com/contact-us/','https://www.rohrer.com/about-us/locations/','https://www.storopack.us/company/about-us/storopack-worldwide/',
'https://www.amcor.com/careers/job-details/req_96546','https://www.amcor.com/careers/job-details/req_96924',
'https://mauserpackaging.com/about-mauser/locations/','https://join.reynoldsconsumerproducts.com/jobs/3753?lang=en-us',
'https://careers.cooperstandard.com/job/16061424/3rd-shift-toolmaker-gaylord-mi/',
'https://www.techniplas.com/','https://www.pactiv.com/']
if __name__=='__main__':
 roots={'https://'+urlsplit(r['operator_website']).netloc+'/' for r in read(H/'input.csv') if r['operator_website']}
 urls=sorted(roots|set(SEEDS))
 with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:fs=list(pool.map(lambda u:fetch(u,refresh=True),urls))
 (H/'fetches.json').write_text(json.dumps(fs,indent=2)+'\n');print('fetched',len(fs),'readable',sum(f['status']=='ok' for f in fs),flush=True)
