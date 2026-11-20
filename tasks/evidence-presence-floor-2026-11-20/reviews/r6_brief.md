# Confirm round 6: V-68 blank-tier fix

Your round-5 finding (High): blank or invalid ecosystem tiers bypassed both V-65 (A/B) and V-68 (C/U). The fix: V-68 now applies to every record whose tier is not A or B. build_baseline.py uses the same predicate and is re-reconciled with the audit (still 858 keys; no record has such a tier today). The new test test_v68_new_ecosystem_record_with_blank_tier_fails appends a row-less ecosystem record with a blank tier and expects the V-68 error. All 6 V-68 tests pass, and validate.py exits 0.

Judge only whether this delta closes your finding without new defects. Return VERDICT: SOUND or UNSOUND, then FINDINGS (file/hunk, concrete failure scenario, severity).

## Delta
diff --git a/scripts/test_validate.py b/scripts/test_validate.py
index a6df72e3..e64c87cb 100644
--- a/scripts/test_validate.py
+++ b/scripts/test_validate.py
@@ -803,6 +803,15 @@ class ValidatorMutationTests(unittest.TestCase):
         self.append_row("organizations_OH.csv", dict(self._rows("organizations_OH.csv")[-1], org_id=new_id, verification_tier="C"))
         self.assert_fails_with(self.V68_MSG.format(t="organizations", rid=new_id, tier="C"))
 
+    def test_v68_new_ecosystem_record_with_blank_tier_fails(self):
+        # review 2026-11-20 (Codex, round 5): ecosystem has no tier-enum check, so a blank tier must not slip past both
+        # V-65 (A/B) and V-68; V-68 covers every tier that is not A or B.
+        shards = [p.name for p in self.data.glob("organizations_*.csv")] + ["ecosystem.csv"]
+        top = max(int(r["org_id"][4:]) for name in shards for r in self._rows(name))
+        new_id = f"ORG-{top + 1:06d}"
+        self.append_row("ecosystem.csv", dict(self._rows("ecosystem.csv")[-1], org_id=new_id, verification_tier=""))
+        self.assert_fails_with(self.V68_MSG.format(t="ecosystem", rid=new_id, tier="(blank)"))
+
     def test_v68_baselined_record_gaining_a_row_only_warns(self):
         has_rows = self._evidence_index()
         tiers = {r["person_id"]: r["verification_tier"] for r in self._rows("people.csv")}
diff --git a/scripts/validate.py b/scripts/validate.py
index 93f278b2..34006bd2 100644
--- a/scripts/validate.py
+++ b/scripts/validate.py
@@ -694,10 +694,11 @@ def v68_key(table, rid, values):
 _with_rows = {(r["record_table"].strip(), r["record_id"].strip()) for r in evidence}
 for _table, _rows, _idcol, _identcols in V68_TABLES:
     for r in _rows:
-        rid = r[_idcol].strip()
-        if (r.get("verification_tier") or "").strip() in ("C", "U") and (_table, rid) not in _with_rows:
+        rid, tier = r[_idcol].strip(), (r.get("verification_tier") or "").strip()
+        # "not A/B", not "in C/U": a blank or invalid tier (ecosystem has no tier-enum check) must not escape both floors
+        if tier not in ("A", "B") and (_table, rid) not in _with_rows:
             debt("V-68", v68_key(_table, rid, [r.get(c) for c in _identcols]),
-                 f"{_table} {rid} is tier {r['verification_tier'].strip()} with no evidence row in data/evidence_*.csv (SCHEMA §4.13 presence floor, V-68)")
+                 f"{_table} {rid} is tier {tier or '(blank)'} with no evidence row in data/evidence_*.csv (SCHEMA §4.13 presence floor, V-68)")
 
 DEBT_DETAILS = "--debt-details" in sys.argv
 for rule in sorted(set(DEBT_FOUND) | set(DEBT_BASELINE)):
diff --git a/tasks/evidence-presence-floor-2026-11-20/build_baseline.py b/tasks/evidence-presence-floor-2026-11-20/build_baseline.py
index 6ea6a41f..46eace41 100644
--- a/tasks/evidence-presence-floor-2026-11-20/build_baseline.py
+++ b/tasks/evidence-presence-floor-2026-11-20/build_baseline.py
@@ -14,7 +14,6 @@ from pathlib import Path
 
 ROOT = Path(__file__).resolve().parents[2]
 DATA, BASELINE = ROOT / "data", ROOT / "scripts" / "validate_debt_baseline.json"
-TIERS = ("C", "U")
 # must stay identical to scripts/validate.py V68_TABLES / v68_key (validate.py proves it: 0 new V-68 errors after a write)
 TABLES = {"organizations": ("organizations_*.csv", "org_id", ("legal_name", "hq_city", "hq_state")),
           "sites": ("sites_*.csv", "site_id", ("org_id", "site_name", "street_address", "city", "state")),
@@ -36,7 +35,7 @@ def rows(pattern):
 
 with_rows = {(r["record_table"].strip(), r["record_id"].strip()) for r in rows("evidence_*.csv")}
 keys = sorted(v68_key(t, r[col].strip(), [r.get(c) for c in ident]) for t, (pat, col, ident) in TABLES.items()
-              for r in rows(pat) if (r.get("verification_tier") or "").strip() in TIERS and (t, r[col].strip()) not in with_rows)
+              for r in rows(pat) if (r.get("verification_tier") or "").strip() not in ("A", "B") and (t, r[col].strip()) not in with_rows)
 assert len(keys) == len(set(keys)), "duplicate record key"
 by_table = Counter(k.split(":", 1)[0] for k in keys)
 
@@ -46,7 +45,7 @@ audit = json.loads(subprocess.run([sys.executable, str(ROOT / "scripts" / "audit
                                   capture_output=True, text=True, encoding="utf-8", check=True, cwd=ROOT).stdout)
 audit_by_table = Counter()
 for s in audit["summary"]:
-    if s["tier"] in TIERS:
+    if s["tier"] not in ("A", "B"):  # same predicate as validate.py V-68 (blank or invalid tiers fall in)
         audit_by_table[s["table"]] += s["no_rows_history_unknown"]
 print("baseline:", len(keys), dict(sorted(by_table.items())))
 print("audit   :", sum(audit_by_table.values()), dict(sorted(audit_by_table.items())))
