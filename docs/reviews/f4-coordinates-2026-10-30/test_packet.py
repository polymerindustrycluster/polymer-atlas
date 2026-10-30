"""Run: python3 -m unittest discover -s docs/reviews/f4-coordinates-2026-10-30 -p 'test_*.py'."""
import unittest,csv,json,pathlib,hashlib,subprocess,sys
sys.path.insert(0,str(pathlib.Path(__file__).parent))
from process import compare,county_norm,norm
from prepare import disposition
P=pathlib.Path(__file__).parent
class PacketTests(unittest.TestCase):
 def test_population_and_requests(self):
  p=list(csv.DictReader(open(P/'population.csv')));req=list(csv.reader(open(P/'request.csv')))
  self.assertEqual(len(p),1517);self.assertEqual(len({r['site_id'] for r in p}),1517)
  self.assertEqual({r['site_id'] for r in p if r['input_status']=='REQUESTED'},{r[0] for r in req})
  self.assertEqual(len(req),1476)
  raw=list(csv.reader(open(P/'response.csv')));self.assertEqual(len(raw),1476);self.assertEqual({r[0] for r in raw},{r[0] for r in req})
 def test_no_canonical_changes(self):
  m=json.load(open(P/'manifest.json'))
  for path,h in m['canonical_sha256'].items():self.assertEqual(hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest(),h,path)
  self.assertEqual(subprocess.check_output(['git','diff',m['pin'],'--','data/']),b'')
 def test_one_output_per_site_and_no_held_coordinates(self):
  pop=list(csv.DictReader(open(P/'population.csv')));rows=list(csv.DictReader(open(P/'coordinates-packet.csv')))
  self.assertEqual({r['site_id'] for r in pop},{r['site_id'] for r in rows});self.assertEqual(len(rows),1517)
  for r in rows:
   if r['disposition']=='REFERENCE_MATCH':
    self.assertTrue(r['lat'] and r['lng']);self.assertEqual(r['provider_match_type'],'Exact');self.assertEqual(r['address_check'],'PASS_STRICT_NORMALIZED');self.assertEqual(r['precision_class'],'address_interpolated');self.assertTrue(17<float(r['lat'])<72);self.assertTrue(-180<float(r['lng'])<-60);self.assertTrue(r['geocode_source'].startswith('https://geocoding.geo.census.gov/'));self.assertEqual(r['retrieved_at'],'2026-10-30')
   else:self.assertEqual((r['lat'],r['lng'],r['precision_class']),('','',''));self.assertTrue(r['settling_fact'])
 def test_strict_address_safeguards(self):
  r={'street_address':'123 North Main Street','city':'Cleveland','state':'OH','zip':'44101'}
  self.assertEqual(compare(r,'123 N MAIN ST, CLEVELAND, OH, 44101'),'')
  for address,reason in [('125 N MAIN ST, CLEVELAND, OH, 44101','street_mismatch'),('123 S MAIN ST, CLEVELAND, OH, 44101','street_mismatch'),('123 N MAIN ST, AKRON, OH, 44101','city_mismatch'),('123 N MAIN ST, CLEVELAND, PA, 44101','state_mismatch'),('123 N MAIN ST, CLEVELAND, OH, 44102','zip_mismatch')]:self.assertIn(reason,compare(r,address))
 def test_partial_addresses_not_requested(self):
  for street in ['','Industrial Park','Main St','I-75 at Industrial Blvd','123 HWY AT ROAD','PO BOX 42']:
   r={'street_address':street,'latitude':'','longitude':'','notes':'','state':'OH','city':'Akron','zip':''}
   self.assertNotEqual(disposition(r),'REQUESTED')
 def test_county_normalization_never_folds_city_into_county(self):
  self.assertEqual(county_norm('St Louis (City)'),county_norm('St. Louis city'))
  self.assertEqual(county_norm('DONA ANA'),county_norm('Doña Ana County'))
  self.assertNotEqual(county_norm('Baltimore'),county_norm('Baltimore city'))
if __name__=='__main__':unittest.main()
