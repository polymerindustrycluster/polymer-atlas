"""Receipt/proof-gated append, preserving every prior link; idempotent."""
from common import *
from check import main
sys.path.insert(0,str(ROOT/'scripts'))
from shard_io import append_sorted
if __name__=='__main__':
    # Replaying an already applied packet must pass the same proof gate.
    try:packet,outcomes,counts=main(applied=False)
    except AssertionError:
        packet,outcomes,counts=main(applied=True)
    old={r['evidence_id'] for r in house.read(ROOT/'data/archive_links.csv')}
    additions=[r for r in packet if r['evidence_id'] not in old]
    if additions:append_sorted(ROOT/'data/archive_links.csv',additions,'evidence_id')
    house.write(HERE/'archive_links.csv',sorted(packet,key=lambda r:r['evidence_id']),FIELDS)
    house.write(HERE/'outcomes.csv',sorted(outcomes,key=lambda r:r['evidence_id']),['evidence_id','status'])
    (HERE/'counts.json').write_text(json.dumps(counts,indent=2)+'\n')
    checks=[c for p in PROOFS.glob('*.json') if re.fullmatch(r'[0-9a-f]{64}\.json',p.name) for c in json.loads(p.read_text())['checks']]
    refs={r['archive_ref'] for r in packet}
    unique={c['archive_ref']:c for c in checks
            if c['archive_ref'] in refs and c['status']=='ok' and c['http']=='200'
            and same_capture(c['effective_url'],c['archive_ref'])
            and c['page_sha256']==sha((PROOFS/(sha(c['archive_ref'].encode())+'.txt')).read_bytes())}
    assert set(unique)==refs
    house.write(HERE/'capture_checks.csv',[unique[ref] for ref in sorted(unique)],['archive_ref','status','http','effective_url','checked_at','page_sha256'])
    main()
    print('added',len(additions))
