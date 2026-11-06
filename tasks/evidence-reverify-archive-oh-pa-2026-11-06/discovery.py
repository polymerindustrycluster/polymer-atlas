"""Run only after PIC18 worker exits: same paced CDX/SPN code, separate resumable outputs."""
import importlib.util
import sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
BASE=HERE.parent/'evidence-reverify-archive-2026-11-06'
sys.path.insert(0,str(BASE))
spec=importlib.util.spec_from_file_location('archive_discovery',BASE/'discovery.py')
worker=importlib.util.module_from_spec(spec);spec.loader.exec_module(worker)
for state in ('OH','PA'):
    worker.HERE=HERE/state
    print('ARCHIVE PHASE',state,flush=True)
    worker.main(results=ROOT/f'build/l1-discovery-{state}', output=ROOT/f'build/l1-cdx-links-{state}.csv')
