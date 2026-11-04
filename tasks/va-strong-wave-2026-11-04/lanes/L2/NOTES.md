# Lane L2 notes (VA STRONG wave, 2026-11-04)

12 input clusters, 12 verdicts in `verdicts.csv`. No data/ edits, no git.

| Verdict | Count | Clusters |
|-|-|-|
| VERIFIED_NEW_SITE | 4 | LF-VA-00136 (Mylar, ORG-004553), 00113 (kp, ORG-000921), 00044 (DuPont Spruance, ORG-000805), 00031 (RTP, ORG-001093) |
| VERIFIED_NEW_ORG | 3 | LF-VA-00206 (HEYCO-WERK USA), 00062 (Reiss Manufacturing), 00142 (Indmar Coatings) |
| REJECT | 5 | closed: 00067 (Hilex Poly Richmond), 00023 (Yokohama Salem); out of scope: 00116 and 00193 (QualiChem), 00203 (FUJIFILM Wako) |
| STILL_UNCERTAIN / DUPLICATE_OF | 0 | |

Every `own_quote` was re-checked against the fetched page text by script (12 of 12 found after whitespace normalization).

## Flags for the integrator

**Closures (REJECT, dated):**
- LF-VA-00023 Yokohama Salem: Yokohama Rubber press release 2026-03-16, plant closed 2026-03-18 (parent site y-yokohama.com; confirmed by Rubber World, The Shop, WDBJ).
- LF-VA-00067 Hilex Poly Richmond: Novolex statement quoted by Virginia Business (May 2026) plus WARN letter dated 2026-05-11, layoffs 2026-07-14 to 2026-09-11; Plastics News 2026-05-14. Evidence is trade press quoting the company, not the company site.
- Form 5500 gate: the cluster carries F5500 EINs for Yokohama only; I did not open EFAST2 filing addresses for either closure. A plan filing cannot outweigh a dated company closure statement, but re-run if the rule is read strictly.

**Held-record problems found:**
- ORG-001093 RTP Company lists hq Gahanna OH; RTP's own Facilities page gives Corporate Headquarters Winona MN.
- ORG-000921 Klockner Pentaplast lists hq Greenville OH (a plant); kp Group address on its site is London.
- ORG-000805 is the multi-site DuPont org (7 sites) but its legal_name reads "DuPont (Circleville plant". There is no DuPont de Nemours parent org; integrator should decide whether to attach Spruance there or rename.
- LF-VA-00044: Spruance campus already holds SITE-003166 (Celanese Zytel) and SITE-005884 (Mylar) at other street addresses. Kevlar/Nomex aramids were reportedly sold to Arclin (search result, unverified), so only Tyvek (flashspun HDPE) is claimed.

**Scope questions (not self-ruled, AGENTS section 2 rule 9):**
- LF-VA-00203 FUJIFILM Wako makes LAL reagents, lab chemicals and the V-50 polymerization initiator for superabsorbent-polymer makers. I rejected it (reagents, no stated >=50% polymer customers) but initiators sit near the pending monomers/intermediates scope ruling (SCHEMA 3.2 B-VOC note).
- QualiChem (00116, 00193): metalworking fluids and private-label water-treatment blending, no polymer. Own site also lists a third Salem address, 616 Idaho Street, not in either cluster. The two clusters are the same company; the site does not say which Salem address makes what.

**HQ / identity notes:**
- LF-VA-00206 HEYCO: org row is the US operator HEYCO-WERK USA Inc.; group parent is HEYCO-WERK Heynen GmbH & Co. KG, Remscheid (HQ per own site). Integrator may prefer the group as the org. org_hq_state = Germany. Injection molding is stated on the group technical-plastics page, not on the Emporia line itself.
- LF-VA-00062 Reiss: own site gives a "Corporate Address (AR/AP)" PO Box in Rumson NJ, not a stated HQ; hq fields left blank.
- LF-VA-00031 RTP: own-site witness is plant_only (facility list); compounding comes from company-level text. Consider tier C if the integrator wants a page that states South Boston's activity.
- LF-VA-00136 Mylar: own site never prints a city next to film manufacturing; the witness is "Hopewell Site, USA" on the certificates page, and the brochure PDF prints 3600 Discovery Drive, Chester VA 23836. No processes tagged.
- kp operates a second Virginia plant at Rural Retreat (per kp release): candidate for a later wave. kp also has a second Gordonsville address (3758 Klockner Road) on its certificate.

## Checks run
Dedupe: `atlas.py dedupe-check` by name+street for all 12, domain for heyco.de, heycousa.com, heyco.com, dupont.com, novolex.com, rtpcompany.com, wakochemicals.com, fujifilm.com, qualichem.com, reiss-mfg.com, indmar.com, mylar.com, kpfilms.com, yokohamatire.com, indmarcoatings.com. Also scanned all VA sites for the Spruance/Salem/Chester/Hopewell/Richmond cities. Own domains for Reiss (reissmfg.com) and Indmar (indmarcoatings.com) were found by search, then checked against the shards by hand. Jina fallback used for heyco.de, kpfilms.com, rtpcompany.com and Mylar pages where direct fetch was empty or blocked; own_url stays the company URL.
