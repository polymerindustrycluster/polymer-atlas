"""Reuse receipt-gated builder; old links stay immutable and outside this packet."""
from check_archives import HERE,house
import build as builder
from check import main as preflight

if __name__=='__main__':
    preflight(applied=False)
    builder.HERE=HERE
    builder.main()
