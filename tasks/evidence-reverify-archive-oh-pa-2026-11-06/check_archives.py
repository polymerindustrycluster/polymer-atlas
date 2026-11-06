"""Fresh gate, including inherited links; zero new continuation links cannot pass."""
from shared import HERE,BASE,house,bound_verdicts
import check_archives as gate

if __name__=='__main__':
    assert house.read(HERE/'new_archive_links.csv'), 'Archive gate incomplete: no new continuation capture verified'
    gate.HERE=HERE
    gate.bound_verdicts=bound_verdicts
    gate.main()
