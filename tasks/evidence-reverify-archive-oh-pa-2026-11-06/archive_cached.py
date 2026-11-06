"""Reuse only existing capture discoveries for OH then PA; no concurrent archive API requests."""
import sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
BASE=HERE.parent/'evidence-reverify-archive-2026-11-06'
sys.path.insert(0,str(BASE))
import archive
sys.argv.append('--cached-only')
for state in ('OH','PA'):
    archive.HERE=HERE/state
    print('CACHED ARCHIVES',state,flush=True)
    archive.main()
