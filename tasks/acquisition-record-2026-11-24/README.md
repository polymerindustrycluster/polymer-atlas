# Acquisition record

Adds `docs/ACQUISITION.md`, the durable record of how the Atlas finds, proves and captures websites, addresses and pages,
with a log of past experiments and their yields. No file under `data/` changes.

First user: the owner and the model families brainstorming what the stack lacks. Non-use review 2026-12-24.

Check: `python3 tasks/acquisition-record-2026-11-24/check.py`. It reads the experiments log, fails on a row whose folder,
file or controller packet does not exist, and fails on a thread id, local path or spend figure in the page. It injects both
defects first and asserts they are caught.
