#!/usr/bin/env python3
"""Idempotent entry point; raw snapshots/indexes stay in the external cache."""
import runpy
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'scripts'))
runpy.run_module('bulk_sources', run_name='__main__')
