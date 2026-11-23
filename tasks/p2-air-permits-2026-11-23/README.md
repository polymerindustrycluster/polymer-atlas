# PIC-18 Ohio EPA permit process fills (G3)

Built by: Codex GPT-6.2 Sol (atlas-p1-integrator-1), 2026-11-23.

Owner round 11 authorized reading Ohio EPA air permits for process.
Round 24 item 3 admits an explicitly named process on a tier A/B site
when the permit names that site's premises and a second family reads
the witness. The permit establishes dated authorization. Plymouth's
initial-installation permit provides no separate commissioning evidence.

The independent reading packet has eight VERIFIED quotes and two REJECT
quotes. The eight witnesses fill six blank Ohio site `processes` cells
on six distinct owners. Three observations support A-tier sites and
five support B-tier sites. Two witness pairs each support one site cell.
Among 794 owners of active tier A–C PIC-18 sites, process-unknown owners
fall from 312 (39.3%) to 306 (38.5%). The ledger has six corrected claims.

## Public citations

The Ohio EPA Air Services eDocument IDs and permit numbers in the
evidence rows identify the filings. The process and premises page numbers
are one-based physical PDF pages. Observed dates are the permits'
effective dates. The reader date is 2026-11-23.

- Custom Pultrusions, eDocument [4359369](https://edocpub.epa.ohio.gov/publicportal/ViewDocument.aspx?docid=4359369), P0139216.
- Mitsubishi Chemical, eDocument [2242238](https://edocpub.epa.ohio.gov/publicportal/ViewDocument.aspx?docid=2242238), P0133817.
- Plymouth Foam, eDocument [3267030](https://edocpub.epa.ohio.gov/publicportal/ViewDocument.aspx?docid=3267030), P0135276.
- Ventra Salem, eDocument [4023003](https://edocpub.epa.ohio.gov/publicportal/ViewDocument.aspx?docid=4023003), P0138283.
- Trans-Foam, eDocument [3792297](https://edocpub.epa.ohio.gov/publicportal/ViewDocument.aspx?docid=3792297), P0137909.
- Blair Rubber, eDocument [1315096](https://edocpub.epa.ohio.gov/publicportal/ViewDocument.aspx?docid=1315096), P0127945.

Ohio EPA permit IDs are named-source citations under SCHEMA §§4.13 and
4.22. The process excerpt is verbatim after whitespace normalization.
The separately labelled premises fields replay from the filing and
allow the structured binding gate to check the operator and street.

## Open queue

Both Ventra Sandusky quotes cite P0134426, which P0136216 superseded.
The independent reader located candidate replacement terms on physical
pages 38 and 51 of eDocument 3391798. The queue requires a separate
current-witness review. Schneller needs a current permit naming its coating
line. NewKor needs dated premises status and an operative witness.
Lincoln's encapsulation mapping awaits a vocabulary ruling or an explicit
polymer process witness. These three prior holds were outside the ten-quote
second read.

## Check

```sh
lockf -k /tmp/polymer-atlas-heavy.lock python3 -I tasks/p2-air-permits-2026-11-23/check.py --at HEAD
```

`PACKET.sha256` records the used files in the two controller packets.
`INPUTS.sha256` records seven PDFs already in the read-only atlas-store.
The check replays document identity, page, quote offset, permit date,
premises, site binding, the six cells and eight witnesses, and the paired
proposal and review verdicts. It also recomputes the PIC-18 owner census.
The snapshot replay uses the November 23 reader adjudication of permit
currency. It covers neither later permit changes nor plant utilization.
