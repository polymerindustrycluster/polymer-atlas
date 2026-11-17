"""Reuse top-up 1 immutable proof restoration against this pass's capture receipts."""
from common import *
sys.path.insert(0,str(ROOT/'tasks/archive-topup-1-2026-11-06'))
# Loaded explicitly because this file shares the prior module's name.
import importlib.util
spec=importlib.util.spec_from_file_location('prior_restore',ROOT/'tasks/archive-topup-1-2026-11-06/restore_proofs.py')
prior=importlib.util.module_from_spec(spec);spec.loader.exec_module(prior)
prior.HERE=HERE;prior.PROOFS=PROOFS
if __name__=='__main__':sys.exit(1 if prior.main() else 0)
