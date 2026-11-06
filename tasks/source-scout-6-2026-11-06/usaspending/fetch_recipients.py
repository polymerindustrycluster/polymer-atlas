"""Page USAspending's recipient category endpoint for FY2025 contract awards procured under NAICS 3252/3261/3262.
Usage: python3 -I fetch_recipients.py OUT.jsonl   (OUT lives under the persist dir, never in the repo)"""
import json,sys,time,urllib.request
API='https://api.usaspending.gov/api/v2/search/spending_by_category/recipient/'
FILTERS={"award_type_codes":["A","B","C","D"],"time_period":[{"start_date":"2024-10-01","end_date":"2025-09-30"}],
 "naics_codes":{"require":["3252","3261","3262"]},"recipient_locations":[{"country":"USA"}]}
def post(page):
 body=json.dumps({"filters":FILTERS,"limit":100,"page":page}).encode()
 for attempt in range(5):
  try:
   req=urllib.request.Request(API,body,{'Content-Type':'application/json','User-Agent':'polymer-atlas-source-scout-6'})
   return json.load(urllib.request.urlopen(req,timeout=90))
  except Exception as e:
   print('retry',page,e,file=sys.stderr);time.sleep(3*(attempt+1))
 raise SystemExit(f'page {page} failed after 5 attempts')
def main(out):
 page=1;n=0
 with open(out,'w') as f:
  while True:
   d=post(page)
   for r in d['results']:f.write(json.dumps(r,sort_keys=True)+'\n');n+=1
   if not d['page_metadata']['hasNext']:break
   page+=1;time.sleep(0.3)
 print('pages',page,'recipients',n)
if __name__=='__main__':main(sys.argv[1])
