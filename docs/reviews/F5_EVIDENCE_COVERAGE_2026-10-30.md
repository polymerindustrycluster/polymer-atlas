# Evidence coverage inventory

Generated date: 2026-10-30
Snapshot label: `eceead3a5a59b7a51d13b2ad61d6070e4cfc9a05` (caller supplied; input digests below identify actual bytes).

## Interpretation and limits

Read-only inventory of all canonical organization, site, ecosystem and program rows, including tombstones, grouped by their recorded verification tier. Counts are not company/establishment headline totals.

- **No rows/history unknown** is not an error: §4.13 grandfathered legacy sources. These CSVs do not identify creation/claim-change time; `last_verified` is not a migration flag. A no-row record might be grandfathered or might need a post-contract journal review. This report cannot decide which.
- **Started with gaps** has at least one evidence row but lacks one or more current-value checklist claim types. Partial legacy touches remain possible; gaps are review signals, not violations or re-grading instructions.
- **Claim rows present** means claim types are represented, not that the facts are true, current, supported at the claimed tier, or free of contradiction. Contradictions and unsupported present claims are reported separately across all observed claim types, including optional claims.
- Checklist mirrors schema §4.13 / validator V-25: organizations existence/address/scope/code; sites add parent; active organizations/sites add activity/liveness; ecosystem existence/address/scope; programs existence/scope and code when CIP is populated. Organization parent changes require journal-specific review; they cannot be inferred from this snapshot.
- Current contradiction uses §4.13 date ordering: contradiction on/after newest support. Platform categories never count as scope support. This is not V-22/V-25 validation, source fetching, source-class adjudication, tier computation, or status adjudication; run `scripts/validate.py` separately.
- Evidence is append-only history. This inventory does not decide whether claim_detail refers to a superseded value; humans must inspect the cited rows and journals. No legacy source strings are parsed into evidence.

## Coverage by record table and recorded tier

| Table | Tier | Record rows | Evidence rows | No rows/history unknown | Started with gaps | Claim rows present | Current contradiction | Unsupported present claim |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| ecosystem | A | 109 | 90 | 64 | 45 | 0 | 0 | 0 |
| ecosystem | B | 44 | 64 | 12 | 32 | 0 | 0 | 0 |
| ecosystem | C | 25 | 4 | 23 | 1 | 1 | 0 | 0 |
| ecosystem | U | 28 | 0 | 28 | 0 | 0 | 0 | 0 |
| organizations | A | 1029 | 585 | 819 | 207 | 3 | 0 | 0 |
| organizations | B | 2540 | 3332 | 1317 | 1221 | 2 | 0 | 0 |
| organizations | C | 587 | 1042 | 229 | 358 | 0 | 0 | 0 |
| organizations | U | 23 | 0 | 23 | 0 | 0 | 0 | 0 |
| programs | A | 50 | 31 | 38 | 0 | 12 | 0 | 0 |
| programs | B | 17 | 32 | 1 | 0 | 16 | 0 | 0 |
| programs | C | 6 | 0 | 6 | 0 | 0 | 0 | 0 |
| sites | A | 982 | 1553 | 652 | 239 | 91 | 0 | 0 |
| sites | B | 3002 | 4811 | 1578 | 1353 | 71 | 0 | 0 |
| sites | C | 1327 | 1289 | 810 | 513 | 4 | 0 | 0 |
| sites | U | 459 | 43 | 451 | 6 | 2 | 0 | 0 |

## Missing claim types among records that already have evidence

One record can contribute several missing claim types; do not sum these as distinct records.

| Table | Missing claim | Record rows |
|---|---|---:|
| ecosystem | address | 78 |
| ecosystem | scope | 1 |
| organizations | activity | 1723 |
| organizations | address | 1542 |
| organizations | code | 1766 |
| organizations | existence | 6 |
| organizations | liveness | 1728 |
| organizations | scope | 46 |
| sites | activity | 543 |
| sites | address | 70 |
| sites | code | 1955 |
| sites | existence | 1766 |
| sites | liveness | 1934 |
| sites | parent | 1829 |
| sites | scope | 422 |

## Bounded review queue

Showing 25 of 3971 active/unknown records with evidence and a gap, unsupported claim or current contradiction. No-row records are excluded to avoid treating grandfathered records as failures. Priority: contradictions, unsupported claims, A–C tiers, missing scope, number of gaps, table and ID. This is research triage, not an entity verdict.

| Table / ID | Name | Tier | Missing | Contradicted | Unsupported | Evidence IDs |
|---|---|---|---|---|---|---|
| sites / SITE-002182 | Ultra-Poly Corporation | B | activity, code, existence, liveness, parent, scope | — | — | EVD-008479 |
| sites / SITE-002532 | Berry Global | B | activity, address, code, existence, liveness, scope | — | — | EVD-000676 |
| sites / SITE-002624 | NPX ONE - Reading Plant | B | activity, code, existence, liveness, parent, scope | — | — | EVD-007080 |
| sites / SITE-002733 | Berry Global Inc. | B | activity, address, code, existence, liveness, scope | — | — | EVD-000690 |
| sites / SITE-002744 | Berry Plastics Corp  -  Erie | B | activity, address, code, existence, liveness, scope | — | — | EVD-000691 |
| sites / SITE-002750 | Bemis Company Inc. | B | activity, address, code, existence, liveness, scope | — | — | EVD-000692 |
| sites / SITE-002801 | Maui Cup A Division Of Letica Corporation | B | activity, address, code, existence, liveness, scope | — | — | EVD-000717 |
| sites / SITE-003231 | Colortech Morristown plant | B | activity, code, existence, liveness, parent, scope | — | — | EVD-007396 |
| sites / SITE-003272 | Teknor Apex - Pawtucket HQ & Plant | B | activity, code, existence, liveness, parent, scope | — | — | EVD-007432 |
| sites / SITE-003285 | Hultec (S&B Technical Products) - Fort Worth Plant | B | activity, code, existence, liveness, parent, scope | — | — | EVD-003335 |
| sites / SITE-003325 | Asahi Kasei Plastics North America - Fowlerville | B | address, code, existence, liveness, parent, scope | — | — | EVD-009855 |
| sites / SITE-003348 | Bay Plastics Machinery HQ & Plant | C | activity, code, existence, liveness, parent, scope | — | — | EVD-003575 |
| sites / SITE-003352 | BYK USA Gonzales | C | activity, code, existence, liveness, parent, scope | — | — | EVD-003579 |
| sites / SITE-003359 | Kuraray America EVAL Plant | A | activity, address, existence, liveness, parent, scope | — | — | EVD-003596 |
| sites / SITE-003360 | Lion Copolymer Geismar Plant | B | activity, code, existence, liveness, parent, scope | — | — | EVD-007192 |
| sites / SITE-003361 | Lion Elastomers Port Neches Plant | A | activity, address, existence, liveness, parent, scope | — | — | EVD-003599 |
| sites / SITE-003362 | Lion Elastomers Orange Plant | B | activity, code, existence, liveness, parent, scope | — | — | EVD-007193 |
| sites / SITE-003370 | Passaic Color & Chemical Plant | A | activity, address, existence, liveness, parent, scope | — | — | EVD-003616 |
| sites / SITE-003376 | Michelin — Greenville (US1) | A | activity, address, code, liveness, parent, scope | — | — | EVD-003070 |
| sites / SITE-003378 | Michelin — Sandy Springs | B | activity, address, code, liveness, parent, scope | — | — | EVD-006742 |
| sites / SITE-003380 | Michelin — Starr | B | activity, address, code, liveness, parent, scope | — | — | EVD-006741 |
| sites / SITE-003381 | Michelin Aircraft Tire — Norwood | A | activity, address, code, liveness, parent, scope | — | — | EVD-003071 |
| sites / SITE-003383 | Pirelli Tire — Rome (US HQ & MIRS plant) | B | activity, code, existence, liveness, parent, scope | — | — | EVD-007383 |
| sites / SITE-003385 | Continental Tire — Mt. Vernon | A | activity, address, code, liveness, parent, scope | — | — | EVD-003081 |
| sites / SITE-003386 | Continental Tire — Sumter | A | activity, address, code, liveness, parent, scope | — | — | EVD-003082 |

For each candidate: inspect the integration journal to establish whether the prospective contract applies; then observe the original witnesses afresh and submit an evidence packet. Do not promote, demote, merge or change status from this report.

## Reproduce

```sh
python3 scripts/validate.py
python3 scripts/audit_evidence_coverage.py --as-of 2026-10-30 --snapshot-ref eceead3a5a59b7a51d13b2ad61d6070e4cfc9a05 --limit 25 --format markdown
python3 -m unittest discover -s scripts -p 'test_audit_evidence_coverage.py'
```

Use `--format json` for claim-row counts, structured review records and the same input manifest. Output goes only to stdout; redirect only to a report, never a canonical CSV.

## Input SHA-256 manifest

| CSV | SHA-256 |
|---|---|
| ecosystem.csv | `d76a8d2d588f967290c385e03a5b7926d4491f2d42d96c635b38f1abadcfa9f7` |
| evidence.csv | `7d24b4b7ad42a3e63fc978e1d268f5d05ce5e044c51ad930e7d29f3e82e92e1c` |
| organizations_AL.csv | `d0c9b589b5347efb065db1439a6271837b81f5a0f8efc4bc867bd086dd7feae8` |
| organizations_AR.csv | `64556afbae96f517d3e147c64bbb802523c5ecbdaeed36f6245148c2d5bba62b` |
| organizations_AZ.csv | `ab75553f952ab978ca2075b5c8d98c535d654cf17cd3fbe3d0f7c8e51a53cc13` |
| organizations_CA.csv | `6382e9c5e9b116bb73b40b50514c1cae67bd41c7680e711d8b8499225c24a907` |
| organizations_CO.csv | `a063cf26c927d8a24c1d834e5d9460b92e6e8059ba2d4746c1b0aa3475903417` |
| organizations_CT.csv | `b38e2ec31ef58cee19bdf057cc298d406e6b4dcfee3c41174691b9fd91da3dba` |
| organizations_DE.csv | `92b43fb3d2e9e8e3a0b6594cc22172544357a98b9062eb20122942dc0acf45ca` |
| organizations_FL.csv | `fc0c47687937c1baac05bf6e3afd3d07132159a80d0f0fdc041d3bbea147b3b0` |
| organizations_GA.csv | `fbc83a01d6922b4b288b55901ad86603ebbd907e8dfe818db915c4c8fb5a4d12` |
| organizations_IA.csv | `0d565f5ee140ca56622516c0ed37795885dd80536a2a26c86d6b086bfd69eb3d` |
| organizations_ID.csv | `7fbc40e9e86b47263ce15614c9faa813843acf77a7b69c0711cb68747a8ab636` |
| organizations_IL.csv | `c3f8ef7104706c740383e50920eb1162ca3c86bce02d0188b47e0134e3a4e325` |
| organizations_IN.csv | `af3f1c294cc841f55549eae8ae642f2452ca707e2ff623bf347163cf4839742a` |
| organizations_INTL.csv | `54945ebb1fd0dd8006015af222060731b1db84c3e5dc0f047b8ec7ede6455470` |
| organizations_KS.csv | `8caa391d2c461bb27fd64db3bac8a7cd3de51404faee2d3134af96f9aad0142f` |
| organizations_KY.csv | `caeb2bde8254ffbbb952f720b5fdb1b9f22e1e3b2cbb9a1ee8450affacca416a` |
| organizations_LA.csv | `83f0ebee9abbcb9450c48906c9fb66967dd7ff32c02c229f987396be4c8a7d56` |
| organizations_MA.csv | `e00851c4de146a218346b0c435bfb21d29639b4dd79ab89b45f11b288378829f` |
| organizations_MD.csv | `f5e4ccb6ac6effb70d0c636d72d87089d8869a64ce3ff8f63a7de4c32d373f7e` |
| organizations_ME.csv | `8c6e93a522be892a780c097600f6452d4ba1e8a8f08ef57d6bed0754f21f62ad` |
| organizations_MI.csv | `913df4d69447b876f91b1f29e1a7a6500236f019a674ad7e5b4937fe46aef0ac` |
| organizations_MN.csv | `19ffbeb8d30319b0fb01d3e15ec3087d59f6c413067e97cf3bef55e63c4569d7` |
| organizations_MO.csv | `1d2ce1d31aad8c79c11dc144e69ba1e79d2f7f9db6865e8c3375daeb1c49685f` |
| organizations_MS.csv | `217bce90b54a9afbb0f190d44d4cb3abea282e03b8db03582e4abe9bef567b11` |
| organizations_MT.csv | `6d9f887b6552d2c25e8deb1d1d0def831838cbd1418d4b692b548e134ec37c0a` |
| organizations_NC.csv | `8134366e3b601f0d218ee708e491bc0d1a5a67e42584072615e7d75d900ea191` |
| organizations_ND.csv | `929cc866ad8454a44d109e41e9eaafbac64e275d0912431b3cf3337cac8be0e7` |
| organizations_NE.csv | `9df0711ce50eb29b498fe241fbd226cfc81a8185a71d2977aac2e33fdc870983` |
| organizations_NH.csv | `d7bd10dbe0694b37b6192c3464a1f51fb90aecad271f49907c7a5960c1f2e778` |
| organizations_NJ.csv | `31065597103cc2a295e7dc21943fa5f671a9efa416a3a90331c4719028aae43f` |
| organizations_NM.csv | `c04d5547c43e3c451c23d2ccdb66373e89ad6301d56bfca7c41913bd14ae17f3` |
| organizations_NV.csv | `635a155cf9ffaf1076d7bce13e5c2a3deabeea4d80a132b3e827c90fecec483b` |
| organizations_NY.csv | `0f03e4f7baec115229e27d7e198d30be9a5255f71038c1e686ae1e159e7deb28` |
| organizations_OH.csv | `147f2fd71afc811d7247344782e44e4583c7cb7e3a22f3a955106fd95bb8757f` |
| organizations_OK.csv | `ee2ed93390b698965eee02ba95dffd60606ac7f1ab5397758817bc1d77ea8af5` |
| organizations_OR.csv | `2b50298ee24e85efdc9d38b61e5ada2795322d994b7b4e3859ee386a22d0c4be` |
| organizations_PA.csv | `7cfeca01b5a5ac3f67879effaf53b3ba31ef2961b80d8e3a2be7036501e18380` |
| organizations_RI.csv | `7f43f72941440936466e12083a3435583fca3c9770588d779227fce0b46a430b` |
| organizations_SC.csv | `3dbbf3cfbf6bf1e8913fd05db3b483d59c78d333c09e9b6f163506cf8e4b4a2a` |
| organizations_SD.csv | `72821b91e21b02e249ce9f8b15ed9756bdefa269921a97cc88d9fddc787f4aad` |
| organizations_TN.csv | `805e9b0be1b89004bdb58d5c36023b47f6b516a7393b08d43163c1a9234c7ca1` |
| organizations_TX.csv | `e661e058811619e80b299d4a9d45ffbcac07bdee8172363021f07087c7c21f7d` |
| organizations_US.csv | `c42e32183f515d59ff2e4ddb8390c0ff33a70b05c3080e710690f891dcbd4407` |
| organizations_UT.csv | `8f750b6df20a2c7ff6e6c148d46653fbdb4424711ea82dbcf51441c4ed16c5c0` |
| organizations_VA.csv | `c4ad595ef65a457f34597e21f83703770eb566c83b6693eac1b7c29d4e6302f5` |
| organizations_VT.csv | `649873b53e943e0df0df8235fadaf220d37a3375da1c86c463b00143a78c713b` |
| organizations_WA.csv | `0e8994b6425a755915349e809bd04f0f606d0d4c53d926ed710792096ca93d38` |
| organizations_WI.csv | `b135e297a759f5182c6c36315130fce1753bd7ace81224dda6cab2dfa68747b1` |
| organizations_WV.csv | `c74ce38e481e63690aa551f567ac50285ac006da54c9d6c5e64543ff2794aee7` |
| organizations_WY.csv | `8d68430cda2c2747369cbfddaf0e2541391b91b833467c76c891920d17dec6cc` |
| programs.csv | `a99d2ed8c6f7c22c6a6ab7071275d28fc91becfd666378eea0ac624c58b29e7d` |
| sites_AL.csv | `4685afe30d84e2b55748d340f3b5235be391a5bea977e20d72d643be350a5b65` |
| sites_AR.csv | `538b58bd73df12eca081e902584fda846bd1deb096fd7afc3d9b974b50e7b662` |
| sites_AZ.csv | `d088e10d63f33048461f8bc06f6e1a924cb8a57956feec9cee1060c1d0183b48` |
| sites_CA.csv | `4354568d67dc8ea08f9cf760da0fd8c04a17eb2b13e7e2cf85f88ef881cc0525` |
| sites_CO.csv | `7793f18e1e530106854105a33085d149239c57f3f47f6b98d3664bb1cb25e605` |
| sites_CT.csv | `af633bcc553db58e8fa5d6ffbc4fb978a96a4fa8b8c0af0e69cc6351c4ae281d` |
| sites_DE.csv | `df1d782ebb0b51f31e4717c0a8f6768439529d7d48dc73e0428cd09808ecdf2b` |
| sites_FL.csv | `982136577a43ef8a1e2ba5d80b36a71746123e14bf46392bf10462f52c388738` |
| sites_GA.csv | `10a62b415abbde4aa6521ad611d6bca7fd59bef70375929b73eb51f1ed789283` |
| sites_IA.csv | `8b9ac230475b2c7c268b8983eef9067345fb4e3f90965b0d0426f5fb8477bcba` |
| sites_ID.csv | `52425dc9183443d8bd7e3444eb019975c9c27d8896b016a26f0b18476cd1ef6e` |
| sites_IL.csv | `f862ec3a299044449776a6350a6fd3318c36edf408dd1e14c2a6ce8467b4150a` |
| sites_IN.csv | `112f95538b46357aa392d7cf831b5b322de1bbf409df64f8e1973cd487c39506` |
| sites_INTL.csv | `3965e4be5debdc72201ae2684d40a3bcc8fef09c1bccf0ca764c51366e17898d` |
| sites_KS.csv | `c3b1e60d2c91a578118300ccbd49a67246720d25943f2c369577002646715c64` |
| sites_KY.csv | `e60d875ee257d61a71f029fb0b87a0d4c027e0a49607e5dfbeaae5ba766d154a` |
| sites_LA.csv | `49c6e5d1766513dd194d3980678861d84943036ad9ef18a9ec9b9c95cc3c41be` |
| sites_MA.csv | `c2e37dda34be4b2cd9c6b9824f02e6758e6cec6ac3ea3a20e2b38ecdb9101da7` |
| sites_MD.csv | `e6c2f1e824ab118b0b8f5a1a893f04df24954a7c04f38d2d1e2385242b89ffb6` |
| sites_ME.csv | `f2509ba278ec304dfa43ea3313cacf705ba1576d5d60f29718a6b20099b87cac` |
| sites_MI.csv | `b97f64d75054ab17b3700697dda6b3a1cf3a96e2dd1bb2759bbcfceb40048a9e` |
| sites_MN.csv | `372fa855ad0eb68c520d7377b7d612d24759c3fea0f89b4d784642d8c1eee341` |
| sites_MO.csv | `82f2917edbaf5db361aca6ba107f030728de96b250cfaa1bfc1ac028f5a8bb1c` |
| sites_MS.csv | `6e0f355d199b10216b86aafd3f319756a98e8eef82f7cc003e7f4a3ffd1ef1ae` |
| sites_MT.csv | `36db5167a956e5594d33b12997d1f4ad9a0dec396c231ef6b54356ac84c9e93e` |
| sites_NC.csv | `42c2fe999ed4f9178fdce9fc64bf871daf254f08a367cfd1287f874e49f8b50a` |
| sites_ND.csv | `a6bd21a3b86102977fd15a03f5357f1f4b6b010348727f2561eada0b4d763e2f` |
| sites_NE.csv | `98b7559599fd2e988f1975b5bfa05f086544574789bb28ec280b60f69f5eeba5` |
| sites_NH.csv | `f62f07c3bde8a433c4e8f6ae465e07700d2b87b383dad5afbb5ad89f008ccf12` |
| sites_NJ.csv | `192c267444db2bff3b489f87c2e1b888f9f4b05c0b8c953952be2df835b269d3` |
| sites_NM.csv | `7ad851e6e47e96b3523185bd4616d058911fffd617c875ef150426ccdf3170c4` |
| sites_NV.csv | `68b1c5e78efd6bd892e5e6157640314e8fdd034cab4c896acac1a395c666c634` |
| sites_NY.csv | `6e33b6da3cf2c023a650484ade3fcce6f206d547513afb80428b44f735319fc4` |
| sites_OH.csv | `2f761c1ee1ac35cf20f83b15d17f7aa125c538111799a5c53c586881343f06eb` |
| sites_OK.csv | `45845bb8978d39d16b53936c3e2b7a6b14025ed065a5ada8f45db350669d314d` |
| sites_OR.csv | `1bda82e0297545118d12b7a1f117befce148726b0a3e2621f4f56046c6a3f16c` |
| sites_PA.csv | `1bde054778e5633338a05bbb54d399dde4746c8d7e9f101e6b49a2bde28724e6` |
| sites_PR.csv | `3f029ab84649542ff4713b6bb91718f2c45ff2c5b1ae9cc5aff844fe9bd60ede` |
| sites_RI.csv | `d8ed309890d4a47ff0fa5dc2dfe9178e42540368cb797c61e712de35231c1760` |
| sites_SC.csv | `f3176a889604e53da184c0882b614f80083e2e656b296a0318a5add8aa351b5b` |
| sites_SD.csv | `ad3d5fb2a584acd1507e811dc64f751f3e1ce0ede7a3834f40272c0e81d74312` |
| sites_TN.csv | `8c00c7bab238cf907ce41a98a34a47010a15e758afdd4218ea5af8c59618bded` |
| sites_TX.csv | `14dcb958080ffec7e7abfcbc4aada29a11e7faa08d561b8882a63d689027c348` |
| sites_UT.csv | `8db9f09a07b0782d0dee5cbcd09cc88d20173fd75f1af05efdd19633d129dbe2` |
| sites_VA.csv | `7aed722e78b62238a941bc53ce5e96a3ea99fb6b0d36c4de23c6f8a3239f087e` |
| sites_VT.csv | `53d7fd04f2090388cf9a2005feb0da13b34e3eb82b74f1fd47bc1c0459f7ff9f` |
| sites_WA.csv | `ac5e48f5de8446544511495ab673a14be5429c96e7c535abdcb108af936dca45` |
| sites_WI.csv | `e2630ebce363b8e5ed67cfb1741f317879db03b4b2f7e5bc031fc04f5e98245c` |
| sites_WV.csv | `d639ccd6b091548d18caf3c4c38dd97c07ce4a3afef41ad5c2287c1868eaee02` |
| sites_WY.csv | `7fbdfc0650994363c5be2bae54b245152fb5a9bd36b4e83e30bc53c10352dbb5` |
