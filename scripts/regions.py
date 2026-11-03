"""Reporting regions (AGENTS.md section 8). The single source of truth for county sets used by the site,
the explorers and reports. Records never carry a region: they carry a county, and reports apply a region.

PIC-18 (owner ruling 2026-11-03) is the NEO-SMART 18-county Northeast Ohio region. It is the union of the two
JobsOhio network regions that cover it, per https://www.jobsohio.com/ohio-regional-network (read 2026-11-03):
Team NEO (14 counties) and Lake to River (4 counties). The NEO-SMART map (case.edu/neo-smart; the CSU Levin
fact sheet) shades the same 18 counties.

PIC-12 is the earlier cluster definition. It is kept so reports dated before 2026-11-03 stay reproducible;
it is not used for new reporting.
"""
TEAM_NEO = ["Ashland", "Cuyahoga", "Erie", "Geauga", "Huron", "Lake", "Lorain", "Medina", "Portage",
            "Richland", "Stark", "Summit", "Tuscarawas", "Wayne"]
LAKE_TO_RIVER = ["Ashtabula", "Columbiana", "Mahoning", "Trumbull"]
PIC18 = sorted(TEAM_NEO + LAKE_TO_RIVER)
JOBSOHIO_REGION = {**{c: "Team NEO" for c in TEAM_NEO}, **{c: "Lake to River" for c in LAKE_TO_RIVER}}

PIC12 = ["Ashtabula", "Cuyahoga", "Geauga", "Lake", "Lorain", "Mahoning", "Medina", "Portage", "Stark",
         "Summit", "Trumbull", "Wayne"]  # historical (before 2026-11-03)

REGION = PIC18
REGION_LABEL = "PIC-18"

assert len(PIC18) == 18 and set(PIC12) < set(PIC18)
