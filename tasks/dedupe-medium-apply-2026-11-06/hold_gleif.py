#!/usr/bin/env python3
"""Regenerate hold_SND-0101_gleif.csv: the two GLEIF golden-copy records for US Farathane (held fold SND-0101).

Reads the cached GLEIF golden copy (cache/bulk/lei.sqlite, 2026-11-06 08:00 publication, zlib-compressed JSON payloads) by LEI.
Public registry data, no personal data. Run only to refresh; check.py reads the committed CSV.
"""
import csv
import json
import sqlite3
import zlib
from pathlib import Path

HERE = Path(__file__).resolve().parent
DB = Path("/Users/johnswanson/.bb/thread-storage/thr_9i2c6byhcz/2026-11-06-atlas/cache/bulk/lei.sqlite")
LEIS = ["549300P7GW6TNUHX2L07", "549300HLVY1RVM0MPI20"]
FIELDS = [("legal_name", "Entity.LegalName"), ("legal_city", "Entity.LegalAddress.City"), ("legal_region", "Entity.LegalAddress.Region"),
          ("registration_authority", "Entity.RegistrationAuthority.RegistrationAuthorityID"),
          ("authority_entity_id", "Entity.RegistrationAuthority.RegistrationAuthorityEntityID"), ("entity_status", "Entity.EntityStatus"),
          ("entity_creation_date", "Entity.EntityCreationDate"), ("initial_registration_date", "Registration.InitialRegistrationDate"),
          ("registration_status", "Registration.RegistrationStatus"), ("validation_sources", "Registration.ValidationSources")]
db = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
with open(HERE / "hold_SND-0101_gleif.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.writer(fh, lineterminator="\n")
    w.writerow(["lei"] + [f for f, _ in FIELDS])
    for lei in LEIS:
        p = json.loads(zlib.decompress(db.execute("select payload from records where id=?", (lei,)).fetchone()[0]))
        w.writerow([lei] + [p.get(k, "") for _, k in FIELDS])
print(open(HERE / "hold_SND-0101_gleif.csv").read())
