"""Apply reviewed navigation URLs; fail on conflicting values; safe to rerun on fresh main."""
import csv, io
from discover import HERE, ROOT, domain

def main():
    verdicts=list(csv.DictReader(open(HERE/'verdicts.csv')))
    assert len({r['org_id'] for r in verdicts})==len(verdicts)
    edits={r['org_id']:r for r in verdicts if r['verdict']=='VERIFIED'}
    assert edits
    found=set(); writes=[]; cells=0
    for path in sorted((ROOT/'data').glob('organizations_*.csv')):
        if path.name=='organizations_all.csv': continue
        rows=list(csv.DictReader(io.StringIO(path.read_text()))); header=list(rows[0]) if rows else None
        changed=False
        for row in rows:
            if row['org_id'] not in edits: continue
            v=edits[row['org_id']];found.add(row['org_id'])
            assert row['status']=='active' and row['tier1_qualifier'],row['org_id']
            website=row['website'] if '://' in row['website'] else 'https://'+row['website']
            assert website==v['website'],row['org_id']
            assert domain(v['newsroom_url'])==domain(website)
            for col in ('newsroom_url','newsroom_feed_url'):
                value=v[col]
                if not value: continue
                assert row[col] in ('',value),(row['org_id'],col,'conflict')
                if row[col]!=value:row[col]=value; changed=True; cells+=1
        if changed:
            buf=io.StringIO();w=csv.DictWriter(buf,fieldnames=header,lineterminator='\n');w.writeheader();w.writerows(rows);writes.append((path,buf.getvalue()))
    assert found==set(edits),(set(edits)-found)
    for path,text in writes:path.write_text(text)
    print(f'{len(edits)} active tier1 organizations; {cells} cells changed; {len(writes)} shards written')
if __name__=='__main__':main()
