"""Rebase website changes must not inherit old-domain liveness scores."""
import contextlib
import io
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import build
from federal_signals import read, write

class WebsiteRerunTests(unittest.TestCase):
    def test_changed_and_unchanged_domains(self):
        for website,signal,score in [('https://old.example.com/','NXDOMAIN','30'),('https://new.example.com/','WEBSITE_CHANGED_SINCE_SWEEP','0')]:
            with self.subTest(website=website), tempfile.TemporaryDirectory() as d:
                root=Path(d); task=root/'tasks/liveness'; (root/'data').mkdir(); (task/'sweep').mkdir(parents=True)
                sponsor=root/'tasks/form5500-spine-2026-11-01'; sponsor.mkdir()
                write(root/'data/organizations_OH.csv',[dict(org_id='ORG-TEST',legal_name='Test',status='active',website=website)],['org_id','legal_name','status','website'])
                write(root/'data/ecosystem.csv',[],['org_id','legal_name','status','website'])
                write(sponsor/'sponsors.csv',[dict(ein='123456789',latest_filed_plan_year_any='2024',latest_py_all_final_or_short='0')],['ein','latest_filed_plan_year_any','latest_py_all_final_or_short'])
                write(task/'registry_links_snapshot.csv',[dict(org_id='ORG-TEST',site_id='',registry='EIN',registry_id='123456789')],['org_id','site_id','registry','registry_id'])
                write(task/'tri_years.csv',[],['trifid','latest_year','coverage'])
                write(task/'sweep/signals.csv',[dict(org_id='ORG-TEST',domain='old.example.com',signal_class='NXDOMAIN',final_url='')],['org_id','domain','signal_class','final_url'])
                with patch.multiple(build,HERE=task,ROOT=root),contextlib.redirect_stdout(io.StringIO()): build.main()
                row=read(task/'signals.csv')[0]
                self.assertEqual((row['signal_class'],row['score']),(signal,score))
                self.assertEqual(row['sweep_domain'],'old.example.com')
                self.assertEqual(row['current_website'],website)

if __name__=='__main__': unittest.main()
