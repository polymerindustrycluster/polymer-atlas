# Evidence coverage inventory

Generated date: 2026-10-30
Snapshot label: `b67b1924368d60b45a0cb49134ae81ce6b1b0d8c` (caller supplied; input digests below identify actual bytes).

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
| ecosystem | C | 25 | 1 | 24 | 1 | 0 | 0 | 0 |
| ecosystem | U | 28 | 0 | 28 | 0 | 0 | 0 | 0 |
| organizations | A | 901 | 312 | 822 | 76 | 3 | 0 | 0 |
| organizations | B | 2096 | 2401 | 1322 | 772 | 2 | 0 | 0 |
| organizations | C | 475 | 812 | 229 | 246 | 0 | 0 | 0 |
| organizations | U | 23 | 0 | 23 | 0 | 0 | 0 | 0 |
| programs | A | 50 | 14 | 43 | 0 | 7 | 0 | 0 |
| programs | B | 17 | 32 | 1 | 0 | 16 | 0 | 0 |
| programs | C | 6 | 0 | 6 | 0 | 0 | 0 | 0 |
| sites | A | 830 | 1042 | 662 | 77 | 91 | 0 | 0 |
| sites | B | 1969 | 1530 | 1654 | 244 | 71 | 0 | 0 |
| sites | C | 986 | 299 | 812 | 170 | 4 | 0 | 0 |
| sites | U | 459 | 43 | 451 | 6 | 2 | 0 | 0 |

## Missing claim types among records that already have evidence

One record can contribute several missing claim types; do not sum these as distinct records.

| Table | Missing claim | Record rows |
|---|---|---:|
| ecosystem | address | 78 |
| ecosystem | scope | 1 |
| organizations | activity | 1032 |
| organizations | address | 871 |
| organizations | code | 1074 |
| organizations | existence | 4 |
| organizations | liveness | 1037 |
| organizations | scope | 38 |
| sites | activity | 391 |
| sites | address | 32 |
| sites | code | 341 |
| sites | existence | 235 |
| sites | liveness | 321 |
| sites | parent | 248 |
| sites | scope | 242 |

## Bounded review queue

Showing 25 of 1666 active/unknown records with evidence and a gap, unsupported claim or current contradiction. No-row records are excluded to avoid treating grandfathered records as failures. Priority: contradictions, unsupported claims, A–C tiers, missing scope, number of gaps, table and ID. This is research triage, not an entity verdict.

| Table / ID | Name | Tier | Missing | Contradicted | Unsupported | Evidence IDs |
|---|---|---|---|---|---|---|
| sites / SITE-002532 | Berry Global | B | activity, address, code, existence, liveness, scope | — | — | EVD-000676 |
| sites / SITE-002733 | Berry Global Inc. | B | activity, address, code, existence, liveness, scope | — | — | EVD-000690 |
| sites / SITE-002744 | Berry Plastics Corp  -  Erie | B | activity, address, code, existence, liveness, scope | — | — | EVD-000691 |
| sites / SITE-002750 | Bemis Company Inc. | B | activity, address, code, existence, liveness, scope | — | — | EVD-000692 |
| sites / SITE-002801 | Maui Cup A Division Of Letica Corporation | B | activity, address, code, existence, liveness, scope | — | — | EVD-000717 |
| sites / SITE-003285 | Hultec (S&B Technical Products) - Fort Worth Plant | B | activity, code, existence, liveness, parent, scope | — | — | EVD-003335 |
| sites / SITE-003348 | Bay Plastics Machinery HQ & Plant | C | activity, code, existence, liveness, parent, scope | — | — | EVD-003575 |
| sites / SITE-003352 | BYK USA Gonzales | C | activity, code, existence, liveness, parent, scope | — | — | EVD-003579 |
| sites / SITE-003359 | Kuraray America EVAL Plant | A | activity, address, existence, liveness, parent, scope | — | — | EVD-003596 |
| sites / SITE-003361 | Lion Elastomers Port Neches Plant | A | activity, address, existence, liveness, parent, scope | — | — | EVD-003599 |
| sites / SITE-003370 | Passaic Color & Chemical Plant | A | activity, address, existence, liveness, parent, scope | — | — | EVD-003616 |
| sites / SITE-003376 | Michelin — Greenville (US1) | A | activity, address, code, liveness, parent, scope | — | — | EVD-003070 |
| sites / SITE-003381 | Michelin Aircraft Tire — Norwood | A | activity, address, code, liveness, parent, scope | — | — | EVD-003071 |
| sites / SITE-003385 | Continental Tire — Mt. Vernon | A | activity, address, code, liveness, parent, scope | — | — | EVD-003081 |
| sites / SITE-003386 | Continental Tire — Sumter | A | activity, address, code, liveness, parent, scope | — | — | EVD-003082 |
| sites / SITE-003389 | Yokohama Tire Manufacturing Mississippi — West Point | A | activity, address, code, liveness, parent, scope | — | — | EVD-003087 |
| sites / SITE-003391 | Toyo Tire North America Manufacturing — White | A | activity, address, code, liveness, parent, scope | — | — | EVD-003092 |
| sites / SITE-003393 | Nokian Tyres Dayton Factory | B | activity, address, code, liveness, parent, scope | — | — | EVD-003097 |
| sites / SITE-003395 | Giti USA Manufacturing — Richburg | B | activity, address, code, liveness, parent, scope | — | — | EVD-003101 |
| sites / SITE-003474 | Prospira America — Upper Sandusky Plant | B | activity, code, existence, liveness, parent, scope | — | — | EVD-003142 |
| sites / SITE-003480 | Gelest — Glen Rock Plant | B | activity, code, existence, liveness, parent, scope | — | — | EVD-003157 |
| sites / SITE-003483 | Pressure Chemical — Pittsburgh Plant | B | activity, code, existence, liveness, parent, scope | — | — | EVD-003160 |
| sites / SITE-003562 | Belding Tank Technologies - Belding | A | activity, code, existence, liveness, parent, scope | — | — | EVD-003781 |
| sites / SITE-003564 | Edwards Fiberglass - Sedalia | A | activity, address, existence, liveness, parent, scope | — | — | EVD-003782 |
| sites / SITE-003568 | Mateenbar - Concord Plant | C | activity, code, existence, liveness, parent, scope | — | — | EVD-003783 |

For each candidate: inspect the integration journal to establish whether the prospective contract applies; then observe the original witnesses afresh and submit an evidence packet. Do not promote, demote, merge or change status from this report.

## Reproduce

```sh
python3 scripts/validate.py
python3 scripts/audit_evidence_coverage.py --as-of 2026-10-30 --snapshot-ref b67b1924368d60b45a0cb49134ae81ce6b1b0d8c --limit 25 --format markdown
python3 -m unittest discover -s scripts -p 'test_audit_evidence_coverage.py'
```

Use `--format json` for claim-row counts, structured review records and the same input manifest. Output goes only to stdout; redirect only to a report, never a canonical CSV.

## Input SHA-256 manifest

| CSV | SHA-256 |
|---|---|
| ecosystem.csv | `b4120959857961eecba72284f98087d5936c048d20887778ec6f204eba3e64b8` |
| evidence.csv | `50b0ad2dafad4d51fc62814a554f0b1d1ef9f543d7aac65011cd53c81003b64f` |
| organizations_AL.csv | `575d505e2091630c11bdce8026733224e2d2981533a0535cb022527b6278b94b` |
| organizations_AR.csv | `bac4bf4821cbf2e316f40a7704be50dcf4d89df434a813c214ba959c0ab2203d` |
| organizations_AZ.csv | `3fdbd9180c9fd8b4d469c98e76aa735d391fc4e925521f57918293078cfb96dd` |
| organizations_CA.csv | `c0839e70bb569242ddfd91a8176d1c2b8e91b7ec446dc7b00f212efb9926b687` |
| organizations_CO.csv | `e92a14c184ec710730fc658fe06867ec38437ff54eb38b0e3049f9cd76e01daf` |
| organizations_CT.csv | `591e3eeb26715be8443fd696a6fbab73f5aeba2870ca90615df14f6e588ac995` |
| organizations_DE.csv | `feba218ad510fe17008324b3584294c134e674347f13570f9f47c0d4970d5102` |
| organizations_FL.csv | `2c7daf14b0a459214982e834f0890e782ba84493ac536bde7940a4022fd2d196` |
| organizations_GA.csv | `330c55cd890c437b1db8904b8f51707f31695e6af271c2225035a507e4c1a864` |
| organizations_IA.csv | `266c184dd4a191ade77d0f2b5a4f90ab8ac5c359aefd1172b7deb2f33d5f4e4c` |
| organizations_ID.csv | `c3d50277f522a66b7922f742ece764b48e2565cbd57b2ebe4d4a45c5aba51916` |
| organizations_IL.csv | `451edc7f61f2d0b61df66039069c5cbfe5bec606226f093a91b16d1b3199a2b8` |
| organizations_IN.csv | `f9496aa1d3e5059fe76897f0747a4395cbbda0119eefc5a64951013fd66235b9` |
| organizations_INTL.csv | `12a0e63a52f2741a4e51a1b0e8587efdb56e073931020fbf01662760c3318388` |
| organizations_KS.csv | `ebb8f49d1f767226f0bbc7295b66b2b957329bb011d02e623e4d53c1c1b11ce6` |
| organizations_KY.csv | `70c0322918f919708c159177b0467d09b6ca582242b2d6b7096ceabcea83af62` |
| organizations_LA.csv | `70b2bad2330beb421fd3b1d003b551c4e8ba6881160e8d7eb888be33e9a6f1a1` |
| organizations_MA.csv | `e426a1406e8f1988e46a295f26c877685abb81116731d6adf37a11b16d21bab8` |
| organizations_MD.csv | `ba5b4e6261c718cd9f36e0552bcadbc924177739a1354a6d1b983ff3a89f842c` |
| organizations_ME.csv | `b6c5948a40e3ad942cb69e32918e9a34ce7d4029a5e3aef067cc482d725f9bda` |
| organizations_MI.csv | `60af555f58e6dbe382c590824c1a85cfb2ddd272d566e96f621c6478713e643b` |
| organizations_MN.csv | `0da2c624329f5c2eb06c078566a62cd49e52c6c42b93e2b379e2f83d4f1379fe` |
| organizations_MO.csv | `45cd95dd30750288691cbde9a22dcdf37357ee649f5e2dbb9584a3c87a16386f` |
| organizations_MS.csv | `88af8e5c11c133e3f5c3d40618b128c834f46477acaf60532027606ab1d51c5f` |
| organizations_MT.csv | `b004484340208aea3dc5c0b1b106feeeb3a4b358934b4c1564b3227ecf006c01` |
| organizations_NC.csv | `333f9422299d282c0256683b4f5330da12c440d83f1e46a36bb59f1958e9026c` |
| organizations_ND.csv | `f3864590a6dbc54b03db033256f7515e8dd184f80739c1598888a0a65f9fc28c` |
| organizations_NE.csv | `963cf08ff801c6c130550e327bab3036bfeef34cd52c362ce6f63c89c2e36950` |
| organizations_NH.csv | `144c6f96d1c4fdc87f471d94e47a8be8bf14ac045eb9577c6b69d027c0734363` |
| organizations_NJ.csv | `6c1bf2cc09aa9a0368fc86a9a9e99a399f28dd45f8fc44a752bd452590dc5191` |
| organizations_NM.csv | `d0e737e4e16d3963dd993921b5cd9cd47e24723db5fd1ca49096487a78a347a0` |
| organizations_NV.csv | `68d5439bef7a772aa99a5dc372dfff766e8b390b098f245ffb82e1bc66348482` |
| organizations_NY.csv | `a1de857ba1f60cf1536f317df965b132bb6f68325522af9774fe97fd3d383cb1` |
| organizations_OH.csv | `bffbb524719cde24fc97cc94d18bcc8faa158caabd138dd1691fc45b49208bf0` |
| organizations_OK.csv | `9526844876aa32c8b5c483ce5a55487060aad816bcbdc4d4e7f0c1c1ceb4a9f0` |
| organizations_OR.csv | `856dbbbaccd4e028c757190cc710293071a25a78b74740eff7363a1613d9140c` |
| organizations_PA.csv | `accf4a51d6dcba24f874fe72e1b176aae4d68f0fa7ef4a9020552c2d1249ef0f` |
| organizations_RI.csv | `b328927fc1ad7358f1dfd11d4d5f97bae8e1913728c6ec714acd0f02e2a8a2d0` |
| organizations_SC.csv | `4f6382e4cf7996f4018e468ba34d21f8387d3e847c5b71f5ac0030f49e0c6c2c` |
| organizations_SD.csv | `e6f4500d2e4bc731df28c4cc35ee1242d996025c42567a88fc629848025acdff` |
| organizations_TN.csv | `d9a3d72736fe5c4e6daaab1de6a1b44eaa5c10da57d17aa607ecfa57e18044e4` |
| organizations_TX.csv | `ec29ebeec25da6abbe0988038185bdf0af6b14b46c04d9b86beb0f0d4f79d834` |
| organizations_US.csv | `940492f794cc867c6893745b222fd086d2038996696b126d3883ad6d2a624fe4` |
| organizations_UT.csv | `2b339f9e4380ff4edd41a8d0c71954377a744570ff562705199d4e666befe8c8` |
| organizations_VA.csv | `cae65560fb038fe55bd38dc70c74db5deabb012568415201aaaf634d1e5a62d2` |
| organizations_VT.csv | `ba3e144129692ac0cb88f70d5955e42296983e88b5833cc9395c96837b6dd967` |
| organizations_WA.csv | `f9c455c9c2300d18aa63235e56c2d0d826f3cdda1c1c00669c865eca879c0554` |
| organizations_WI.csv | `627cf91fc75a97ac45ca7a52b207a062b7fb323120f1b74e21d4bcdf90d0fdca` |
| organizations_WV.csv | `022b132654cfbb1aa2b4e7e700c6fbe921ebb9a8b952ba757e419da1f3ecdee9` |
| organizations_WY.csv | `a44c019ccb9596215970803ed51ab573728bbbcea3b1ef45aca11eea523037f4` |
| programs.csv | `8dbaea3726b9ff2cb3e2349ddc3201c15467e4cf598f353b369946d9a6188932` |
| sites_AL.csv | `3000713d89aa37972bb572109baddd1cdcdb7a62ccfda005dd8c7b359e35111e` |
| sites_AR.csv | `df6ae04db2acdb672306704b5f0691e810557bb31e3e0661ff20029d5b114b37` |
| sites_AZ.csv | `9ba899097030c2f92a1ad2c263815aebe7aeca52d43e5f596653b1536af70ed5` |
| sites_CA.csv | `d4a04b61144e55de9db3e4178b931a9986d270b0c5c1ad65faa79c4f16db0ccc` |
| sites_CO.csv | `28aa673903a530679a0246b3569933870798f5cb779629286c08bc52081e21d6` |
| sites_CT.csv | `370e45975cb7e732e3790bd7a15ed9ce2d46f86068a26cf610bfea8d7451b9c2` |
| sites_DE.csv | `6cf459062d2f7f799f49ed5151710284c9cf89230263bef8ff1d61cc898442c0` |
| sites_FL.csv | `96f6b7678918bd1e7d490655707563b3d649a235f11b1d61645f7cdc21f0396d` |
| sites_GA.csv | `d047d3a20c581fdadc69796c0dfffd36a6c2899aa741b0ca232efebd75accd75` |
| sites_IA.csv | `2dc45d1314faecdcaad054bb00c6b256fae04ad55f446eb2019347e96e05e2e7` |
| sites_ID.csv | `ab89c526a03bca5af478f424ee1412d0c868e394039f9e21321e8db7e1a31fbb` |
| sites_IL.csv | `d2379e5144f86d5ac420427109271b71c1d4f678fc1532f1bc736a5f311cc147` |
| sites_IN.csv | `172aeda0cdf151403f1691557fdc6674dbafb5e09822e7c369efd918a4b461b9` |
| sites_KS.csv | `d086dd5597ad62bf8454223270d1fdc9f203e52064decd40873174e6d71af1da` |
| sites_KY.csv | `9a7ee704527b6ed0094d8e3ff5d63e2ffda94b3147b0e181ef2ecef2d9296afe` |
| sites_LA.csv | `782533a1f09d436907b1d259597092106647f4ca37b59fe781620d6d4f34f3cf` |
| sites_MA.csv | `9cf9608b9cf4335283356c4ba85c1aa00aaabcd06fefc98fdce40990c208e8a1` |
| sites_MD.csv | `a13b79319e36d6f667d09b71a199dd84f91d9344734ba5908473992e8fcc20c5` |
| sites_ME.csv | `d5eeda0d57cea34054507a108b5c2addc5aaeaa6a080b77183922db1d8c13f30` |
| sites_MI.csv | `a0d19f2349acfaaa77f173d8dc570ae07f19683c37d6f686009d6dd68481bdb9` |
| sites_MN.csv | `53c3cb335347a6df54be70ac36357d14af9ce5d23f43d28204d06121e799d300` |
| sites_MO.csv | `51151dba806c158f648cf955ff0516a64516921355b5cffbd79636437355ccdd` |
| sites_MS.csv | `bb0f2ea664960d17e9516121e8fba2897a711e18561b0adbc3b7dceb007e5e7a` |
| sites_MT.csv | `d8547d0f4dc7b4ab397758c3c429fc3059b0e84d22edc33e8fba9083d519a103` |
| sites_NC.csv | `e84cb780305fd33ce8cba899ffe1b062f42179660c9755494c9240e4e97b1ed0` |
| sites_ND.csv | `e281382263f3032b9a3063a12a107a8f304f24f0b905fb9c6b3fdf9788f2806d` |
| sites_NE.csv | `63c1a6e91227a0c077a46ccda11d00bf654a7c7b91748f570804686b7806a750` |
| sites_NH.csv | `bda4a760e36f90b2f6cfc8978bd398183f9e8200bce3fb49fea96f1a24e5ff06` |
| sites_NJ.csv | `1dd04e5d254677420968408ccda1aeaf367e4216e64ed204cf0f1ffee78d8870` |
| sites_NM.csv | `5a1a9f644e8d774e50cc90119dfdbc2ea1c91a05824e4ff67b1e69eca6ee6978` |
| sites_NV.csv | `bec11eb31b1f9ff61cd851dd26bba5eb4eaf5dc49ad2c59a6390cd8289e45360` |
| sites_NY.csv | `707ebc1eb435ee3bcaef243a8d42c12596011f9136ae321ffc5476ebfcfb1c18` |
| sites_OH.csv | `d09efb125e93da0cbdaf2de71ae3d039202a0c1dba1366a49768e6495438d98c` |
| sites_OK.csv | `42000c99fae28100a4f4d48a27050e2b3f4f61ea42648f73d5dc747d662f46c9` |
| sites_OR.csv | `01c627fce64a6c4d5f013b792e260c79611ca71efdf11e261f3bcc6b0bbec8cb` |
| sites_PA.csv | `fa0537c71ff6d1f115694ece0bcc18c4d94347652a521e74f81e3ebbaeaa493c` |
| sites_RI.csv | `81ab7dd19d1bc81ad204a63a3b057d449bf51129489fe3148067418ed0591dc2` |
| sites_SC.csv | `50d6e777a8d20d4b270c8bd9c5c08ab4e67574920e3e643b9a3a3dc67e52b215` |
| sites_SD.csv | `916ff3f0cfde366085bde9e3d4eecdd1fb716d7763f98b92f4cb93b51f0bfcc6` |
| sites_TN.csv | `25123fb2e8d3e452a21e263f7caad56afe42ee8ab376c534f29894012a68c19c` |
| sites_TX.csv | `80a066de804de7919232aba3e5c2ca7016afc5fa79406c5d9a7d7ffcd0d2a0f2` |
| sites_UT.csv | `ba2f5b254994a9af5771b3e0dee8c73946aa46a4dc05db96d4a55785f209a000` |
| sites_VA.csv | `e69686e25e88c7700fb6a53a119081edc021af3e212d6e35f5909fd3eb58136f` |
| sites_VT.csv | `4f3a7ba1053a344fd3c7823caa5b981ea8dbaf965c0bfb05067e90a3f706fae1` |
| sites_WA.csv | `104bab390764464df9e3501c73be815016ba34937680bc8e0135a095559eb51c` |
| sites_WI.csv | `d610da5c3804ad10143aa07246208769fe231e7008edea689c1fd6c92295236b` |
| sites_WV.csv | `c4c2fc7cffe7930fe42785fb5cf55bafcf7cb27b106de85ce36ec02a68fad6ae` |
| sites_WY.csv | `989641391695b737f4d196c22602090d6b7c36926dddc00bc74dc3a345c27ef5` |
