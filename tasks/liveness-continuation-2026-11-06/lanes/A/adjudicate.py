"""Write explicitly authored proposals; never infer a verdict from retrieved text."""
import csv
from research import HERE,found
FIELDS='rank org_id legal_name verdict finding source_url source_class source_date observed_date quote raw_check fetch_count settling_fact proposed_status successor_org_id ultimate_parent_name grain_hold raw_cache_path'.split()
def put(rank,verdict,finding,settling='',quote='',cache='',source='',source_class='own_site',date='',parent='',grain='',proposed='',successor=''):
    r=next(r for r in csv.DictReader(open(HERE/'input.csv')) if int(r['rank'])==rank)
    logs=[x for x in csv.DictReader(open(HERE/'fetch_log.csv')) if x['org_id']==r['org_id']]
    old=list(csv.DictReader(open(HERE/'verdicts.csv'))) if (HERE/'verdicts.csv').exists() else []
    assert r['org_id'] not in {x['org_id'] for x in old}
    raw='unfetchable'
    if quote:
        from pathlib import Path
        assert found(Path(cache).with_suffix('.txt').read_text(),quote),(rank,quote)
        raw='yes'
    elif any(x['http']=='200' for x in logs): raw='no'
    out=dict(zip(FIELDS,['']*len(FIELDS)))
    out.update(rank=rank,org_id=r['org_id'],legal_name=r['legal_name'],verdict=verdict,finding=finding,source_url=source or r['current_website'],source_class=source_class,source_date=date,observed_date='2026-11-06',quote=quote,raw_check=raw,fetch_count=len(logs),settling_fact=settling,proposed_status=proposed,successor_org_id=successor,ultimate_parent_name=parent,grain_hold=grain,raw_cache_path=cache)
    with open(HERE/'verdicts.csv','a',newline='') as f:
        w=csv.DictWriter(f,fieldnames=FIELDS)
        if not old:w.writeheader()
        w.writerow(out)
if __name__=='__main__':
    put(11,'STILL_UNCERTAIN','Current SRT domain fails DNS by browser-UA curl and Jina; historical Rimflex literature is not current operation.','A current SRT-issued product/order page or dated operating record naming Synthetic Rubber Technologies in Uniontown.')
    put(12,'STILL_UNCERTAIN','Current domain, www variant, and apparent vinylprofiles.com lead fail DNS; association listing and search job lead do not supply raw current primary witness.','A current company-issued extrusion offering or employer-issued operating notice tied to Vinyl Profiles at 11675 Mahoning Avenue, North Jackson.')
    put(13,'STILL_UNCERTAIN','PTC domain unresolved. Search located Kreate-issued 2025-08-25 acquisition release; Business Wire raw route unresolved. Parent-domain secondary reprint excluded from evidence.','Raw Kreate-issued acquisition completion release plus current same Lima operation witness; resolve held acquirer and parent-versus-site grain before status motion.',parent='Kreate (unverified acquisition lead)',grain='HOLD: acquisition identity and operator grain; no successor proposed')
    put(14,'STILL_UNCERTAIN','Vinyltech domain unresolved by curl and Jina; search found historical 2021 extrusion seminar, insufficient for current operation.','A current Vinyltech-issued extrusion-tooling/profile offering or dated operating record at 11635 Mahoning Avenue, North Jackson.')
    put(15,'STILL_UNCERTAIN','Seaway domain fails DNS through HTTPS, HTTP/www and Jina; historical supplier/profile descriptions are not current primary operation.','A current Seaway-issued tooling/mold offering or dated operating record at 5749 Angola Road, Toledo.')
