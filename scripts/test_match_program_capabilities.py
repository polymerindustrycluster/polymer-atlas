import copy
import unittest
from match_program_capabilities import match, geography, vocabulary, ROOT


class MatchTests(unittest.TestCase):
    def setUp(self):
        self.sites = [dict(site_id='S1', org_id='O1', site_name='Plant', operating_status='active', verification_tier='A', state='OH', county='Summit')]
        self.programs = [dict(program_id='P1', institution_org_id='I1', program_name='Lab', program_type='center', status='active', verification_tier='A', state='OH', county='Summit', specialty_processes='injection_molding', specialty_materials='', url='https://example.edu/lab', sources='https://example.edu/lab')]
        self.owners = [dict(org_id=i, status='active', verification_tier='A', legal_name=i) for i in ['O1','I1']]
        self.caps = [dict(capability_id='C1', site_id='S1', org_id='O1', capability_type='process', term='injection_molding', provenance='company_disclosed', source_ref='https://example.com/plant', observed_date='2026-10-30')]
        self.vocab = {'process': {'injection_molding'}, 'material': {'thermoplastics'}}

    def run_match(self): return match(self.sites, self.programs, self.owners, self.caps, self.vocab)
    def count(self): return self.run_match()['summary']['site_program_candidate_pairs']
    def test_positive(self):
        r = self.run_match(); self.assertEqual(self.count(),1)
        self.assertEqual(r['matches'][0]['geography'],'same_county')
        self.assertEqual(r['matches'][0]['candidate_route'],'research_or_facility')
        self.assertEqual(r['matches'][0]['capability_evidence'][0]['source_ref'],'https://example.com/plant')
    def test_no_match(self):
        self.programs[0]['specialty_processes']='polymerization'; self.assertEqual(self.count(),0)
    def test_empty_capabilities(self):
        self.caps=[]; self.assertEqual(self.count(),0)
    def test_no_fuzzy_or_rollup(self):
        self.programs[0]['specialty_processes']='injection_molding_micro'; self.assertEqual(self.count(),0)
    def test_wrong_axis_does_not_match(self):
        self.programs[0]['specialty_processes']=''; self.programs[0]['specialty_materials']='injection_molding'; self.assertEqual(self.count(),0)
    def test_product_form_has_no_program_axis(self):
        self.caps[0]['capability_type']='product_form'; self.assertEqual(self.count(),0)
    def test_invalid_controlled_token(self):
        self.caps[0]['term']='made_up'; self.programs[0]['specialty_processes']='made_up'; self.assertEqual(self.count(),0)
    def test_withdrawn(self):
        self.caps[0]['withdrawn_date']='2026-10-30'; self.assertEqual(self.count(),0)
    def test_statuses(self):
        for status in ('closed','merged','acquired','unknown','idled','pre_revenue',''):
            with self.subTest(status=status):
                self.sites[0]['operating_status']=status; self.assertEqual(self.count(),0)
    def test_tombstone_program(self):
        self.programs[0]['status']='merged'; self.assertEqual(self.count(),0)
    def test_tombstone_operator_and_institution(self):
        for owner in self.owners:
            owner['status']='closed'; self.assertEqual(self.count(),0); owner['status']='active'
    def test_unverified(self):
        for row in (self.sites[0], self.programs[0], *self.owners):
            row['verification_tier']='U'; self.assertEqual(self.count(),0); row['verification_tier']='A'
    def test_training_admissions(self):
        self.programs[0]['program_type']='training'
        self.programs[0]['admissions_status']='not_admitting'; self.assertEqual(self.count(),0)
        self.programs[0]['admissions_status']='unknown'; self.assertEqual(self.run_match()['matches'][0]['readiness'],'admissions_unverified')
        self.programs[0]['admissions_status']='admitting'; self.assertEqual(self.run_match()['matches'][0]['readiness'],'contact_and_scope_check_required')
    def test_mismatch_and_missing_provenance(self):
        self.caps[0]['org_id']='O2'; self.assertEqual(self.count(),0)
        self.caps[0]['org_id']='O1'; self.caps[0]['source_ref']=''; self.assertEqual(self.count(),0)
        self.caps[0]['source_ref']='x'; self.caps[0]['provenance']='directory_assigned'; self.assertEqual(self.count(),0)
    def test_duplicate_id_fails(self):
        self.sites.append(copy.deepcopy(self.sites[0])); self.assertRaises(ValueError,self.run_match)
    def test_multiple_evidence_rows_one_pair(self):
        c=copy.deepcopy(self.caps[0]); c['capability_id']='C2'; self.caps.append(c)
        r=self.run_match(); self.assertEqual(self.count(),1); self.assertEqual(len(r['matches'][0]['capability_evidence']),2)
    def test_deterministic_and_no_mutation(self):
        before=copy.deepcopy((self.sites,self.programs,self.owners,self.caps))
        r=self.run_match(); self.assertEqual(r,self.run_match()); self.assertEqual(before,(self.sites,self.programs,self.owners,self.caps))
    def test_no_distance_or_missing_county_inference(self):
        self.programs[0]['county']=''; self.assertEqual(self.run_match()['matches'][0]['geography'],'same_state')
        self.programs[0]['state']=''; self.assertEqual(geography(self.sites[0],self.programs[0]),'unknown')
    def test_state_filter(self):
        self.programs[0]['state']='PA'; self.assertEqual(self.count(),0)
        self.assertEqual(len(match(self.sites,self.programs,self.owners,self.caps,self.vocab,program_state='')['matches']),1)
    def test_real_vocab_no_alias_expansion(self):
        v=vocabulary(ROOT/'scripts/validate.py')
        self.assertIn('injection_molding',v['process']); self.assertNotIn('extrusion',v['process'])
        self.assertNotIn('carbon_black',v['material'])


if __name__ == '__main__': unittest.main()
