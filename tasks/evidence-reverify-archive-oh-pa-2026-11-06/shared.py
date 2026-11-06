"""Reuse L1's canonical binding and archive gates across the three disjoint frames."""
import sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
BASE=HERE.parent/'evidence-reverify-archive-2026-11-06'
sys.path.insert(0,str(BASE))
import run as house


def bound_verdicts():
    combined={}
    for phase in (BASE,HERE/'OH',HERE/'PA'):
        rows=house.bound_verdicts(phase)
        assert not set(combined)&set(rows), 'overlapping evidence frames'
        combined.update(rows)
    return combined
