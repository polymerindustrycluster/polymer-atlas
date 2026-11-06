"""Freeze conservative final dispositions; readable routes are never absence evidence."""
import csv,json,hashlib
from pathlib import Path
from research import HERE,CACHE,found


def read(p):return list(csv.DictReader(open(p)))


def main():
    inputs=read(HERE/'input.csv');receipts=[r for f in ('fetches.json','followup_fetches.json') for r in json.load(open(HERE/f))]
    verdicts=[];quotes=read(HERE/'degree_research.csv')
    for r in inputs:
        lid=r['lead_id'];fetched=[q for q in receipts if lid in q['lead_ids']];assert fetched,lid
        verdict='STILL_UNCERTAIN';record='';quote='';url=''
        why='Settle with a current institution own named polymer/plastics/composites credential, track, research area or explicit polymer facility offer. Initial route screening only; no absence inference from homepage/failure.'
        if 'CIP ' in r['lead']:why='Settle institution current own named polymer program corresponding to this CIP lead; CIP/completions are not program evidence. Initial institutional route does not settle program scope; obtain its own catalog/track page.'
        elif 'Chapter' in r['lead']:why='Settle named institution own polymer programme independent of the society chapter. Chapter nomination alone cannot evidence programme existence/scope; no programme absence claim.'
        elif 'Bachelor' in r['lead'] or 'Materials' in r['lead']:why='Settle degree own page naming polymer track/concentration/research area. General materials degree or individual polymer courses alone does not settle institutional seam; owner ruling if ambiguous.'
        if lid in ('L13F-025','L13F-026','L13F-027'):
            why='Own current RJG offer and future registration read. HOLD owner scope reading: credential title is Master Molder / Train the Trainer, while description teaches plastic/injection molding. Recommend assess named-polymer test against full own curriculum; do not self-rule whether generic branded credential name satisfies §4.11(a). No new programme created pending ruling.'
        if lid=='L13F-034':why='Own lead URL returned404. Obtain current Routsis named certification offer URL and exact operator/parent identity; failed route is never evidence of discontinuation.'
        if lid=='L13F-040':why='Inherited GONE label is an unverified discovery assertion. Obtain named current catalog +dated operating outcome; Form5500 before any closure REJECT. No closure or status change in this pass.'
        if lid in ('L13F-138','L13F-139'):why='Puerto Rico establishment/schema/program-scope seam: settle institution identity, named polymer offer and lawful geography/schema interpretation. General materials management is not proof of polymer scope; no forced US-state placement.'
        if lid in ('L13F-016','L13F-116'):
            why='Need the institution own named eligible offer independently connected to this SPE student-chapter discovery lead. A held degree page verifies that degree, not the chapter or a duplicate relationship; do not select an arbitrary degree target.'
        verdicts.append(dict(lead_id=lid,source_row=r['source_row'],institution=r['institution'],verdict=verdict,record_id=record,source_url=url,quote=quote,attempt_urls='; '.join(dict.fromkeys(q['url'] for q in fetched)),http_statuses='; '.join(dict.fromkeys(q['http_status'] or '000' for q in fetched)),settling_fact_or_reason=why))
    for name,rows in [('verdicts.csv',verdicts),('holds.csv',[v for v in verdicts if v['verdict']=='STILL_UNCERTAIN']),('quotes.csv',quotes)]:
        with open(HERE/name,'w') as f:
            w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)
    print('169leads:0VERIFIED/0DUPLICATE_OF/169STILL_UNCERTAIN;0canonicalwrites')


if __name__=='__main__':main()
