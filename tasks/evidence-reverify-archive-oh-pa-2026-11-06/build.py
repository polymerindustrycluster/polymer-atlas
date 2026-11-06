"""Apply via PIC18's receipt-gated builder; never overwrite inherited archive links."""
from shared import HERE,house,bound_verdicts
import build as builder

if __name__=='__main__':
    assert house.read(HERE/'new_archive_links.csv'), 'No newly archived continuation evidence to apply'
    builder.HERE=HERE
    builder.bound_verdicts=bound_verdicts
    builder.main()
