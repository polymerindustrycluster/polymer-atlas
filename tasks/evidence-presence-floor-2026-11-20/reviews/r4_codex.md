council-ask: codex effort=deep -> model=gpt-6-astra reasoning=max
VERDICT: UNSOUND

FINDINGS:

- **blocking — `scripts/validate.py`, `V65_TABLES` / V-65 loop:** A contributor can change a baselined, rowless organization’s website/domain while preserving its id, name, city, and state. The fingerprint remains unchanged, so V-65 only warns. This is still a zero-evidence contributor change, even if the entity remains the same. Exempting automated derivation fields is reasonable; the current fingerprint also exempts every substantive nonidentity field. That leaves the stated “creates OR changes” requirement unenforced.

- **nit — `tasks/evidence-presence-floor-2026-11-20/build_baseline.py`, drift-report hunk:** `old - set(keys)` does not establish “now have rows.” Renaming a baselined record without adding evidence produces one supposedly repaired entry and one new violation, although the record remains rowless. Label these obsolete baseline keys, or check evidence presence before reporting them as repaired.
