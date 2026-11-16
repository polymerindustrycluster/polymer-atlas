"""Replay approved data cells onto a main worktree; preflight every file before writing."""
import io
import csv
from pathlib import Path
import sys
from delta_compare import git, table, COMPOSITE


def replay(ref, root):
    root = Path(root)
    base = git(root, 'merge-base', 'origin/main', ref).strip()
    files = git(root, 'diff', '--name-only', base, ref, '--', 'data/').splitlines()
    pending = []
    for name in files:
        if not name.endswith('.csv'):
            raise ValueError(f'{name}: only CSV replay supported')
        hdr, b = table(git(root, 'show', f'{base}:{name}'), name)
        ha, a = table(git(root, 'show', f'{ref}:{name}'), name)
        hm, m = table((root / name).read_text(), name)
        if hdr != ha or hdr != hm:
            raise ValueError(f'{name}: header drift')
        if b.keys() - a.keys():
            raise ValueError(f'{name}: approved rows removed')
        for key, row in a.items():
            if key not in b:
                if key in m:
                    raise ValueError(f'{name}: new key already on main: {key}')
                m[key] = row
                continue
            for col, value in row.items():
                if value != b[key][col]:
                    if key not in m or m[key][col] != b[key][col]:
                        raise ValueError(f'{name}: main changed {key}.{col}')
                    m[key][col] = value
        buf = io.StringIO()
        writer = csv.DictWriter(buf, fieldnames=hdr, lineterminator='\n')
        writer.writeheader()
        writer.writerows(m.values() if (Path(name).name in COMPOSITE or Path(name).name == "inclusion_log.csv") else (m[k] for k in sorted(m)))
        pending.append((root / name, buf.getvalue()))
    for path, text in pending:
        path.write_text(text)


if __name__ == '__main__':
    replay(sys.argv[1], sys.argv[2])
