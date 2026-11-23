# B6 placements for blind audit 12

Built by: Codex GPT-6.2 Sol
Integrator: atlas-p1-integrator-1
Base: `7a9731f2`

The sealed B6 packet covers 31 records that otherwise fit no audit stratum. The
packet contains 34 verdict rows, comprising 31 verified field or placement rows and
three still-uncertain rows. This pass adds eight canonical field fills on six
existing records, six evidence observations and six archive links.
`CLAIMS_CHECKED.csv` records the eight changed canonical cells as corrected.

| Frame disposition | Previously unassignable records |
| --- | ---: |
| PIC-18 | 3 |
| Rest of Ohio | 7 |
| Rest of country | 20 |
| Named exclusion | 1 |
| Still unassignable | 0 |

[placements.csv](../blind-audit-12-protocol-2026-11-23/placements.csv) carries 24
draw-only placements and one named exclusion. This follows owner round 22 and the
controller's applications of B6. The archive links use the authenticated Save
Page Now route from owner round 21.

| Record or group | Disposition |
| --- | --- |
| Hersh Packing & Rubber (ORG-001417) | Franklin County. A separate location page on the company's own site explicitly labels the Canal Winchester headquarters. The Census match is FIPS 39049. |
| ACSIC Ingredients (ORG-001767) | Franklin County, from its contact-page address and the sealed Census match (39049). The page labels it as a contact address and its city matches the held HQ city. |
| World Resource Solutions (ORG-001915) | Union County, from its own street address and the sealed Census match (39159). |
| Youngstown State University (ORG-002175) | Mahoning County, from an own-site University Plaza address and Census match (39099). The Census returned postal ZIP 44502 where the institution uses 44555. Ohio's October 2023 educational-institution directory also places the University Plaza campus in Mahoning County. The packet's search on Tressel Way returned no address match. |
| MKV Polymers (ORG-000095) | Ohio and US from its parent's November 2025 announcement of the planned Akron base, which agrees with the held city and county. Moved from the residual US organization shard to Ohio. |
| The Adhesion Society (ORG-002862) | Alexandria and Virginia come from the same verbatim mailing-style address printed in the organization's copyright line. |
| FLC (ORG-002120) and TechLink (ORG-002122) | Rest of country by their national service scope. Their held office pages could not corroborate the addresses in extracted main text. |
| IACMI (ORG-002099) and REMADE (ORG-002100) | Rest of country by national service scope and the quoted Knoxville and West Henrietta location witnesses. The gate could not bind either address for a canonical update. |
| Ohio Innovation Exchange (ORG-002085 and ORG-002115) | Rest of Ohio under the round 22 city basis. Columbus spans Franklin, Delaware and Fairfield, all outside PIC-18. The Census matched its published street to Franklin. The locator occurs in the footer and could not pass the gate. |
| Mil-Tek (ORG-001850) | PIC-18 by the street-specific Census match to Tuscarawas (39157). Baltic spans the PIC-18 boundary. The live and dated archive contact responses each yielded seven characters in the gate's main-text extraction. |
| JEG and FX Consulting (ORG-001835 and ORG-001503) | Rest of Ohio by Westerville and Dublin under round 22. Their city boundaries span only counties outside PIC-18. |
| Plastics Historical Society (ORG-002872) | Rest of country. Companies House lists the society's registered office in London, England. |
| Side America (ORG-003769) | Named exclusion pending a Sunbiz read that resolves its headquarters. |

The remaining packet placements use the held `geography_served` and the primary
quotes carried in the placement file. The journal records the gate's address
extraction follow-up. Pre-existing MKV `hq_in_scope`, SPE parent locality and
four self-parenting links fall outside the approved correction.

## Replay

The packet checksums are in `PACKET.sha256` and the private capture paths in
`INPUTS.sha256`. `check.py` replays the sealed verdicts and Census responses,
checks the complete canonical cell delta and shard move, and verifies the proof
bytes and claim ledger. The frame check reads the placement list at the pinned
commit and reports the one named exclusion separately.
