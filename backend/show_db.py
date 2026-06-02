import sqlite3, os

root = os.path.dirname(os.path.dirname(__file__))
for dirpath, _, files in os.walk(root):
    if '.venv' in dirpath or 'node_modules' in dirpath:
        continue
    for f in files:
        if f.endswith('.db'):
            path = os.path.join(dirpath, f)
            rel  = os.path.relpath(path, root)
            try:
                conn   = sqlite3.connect(path)
                tables = conn.execute(
                    "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
                ).fetchall()
                size = os.path.getsize(path)
                print(f"\nDB: {rel}  ({size/1024:.1f} KB)")
                for (t,) in tables:
                    cols = conn.execute(f"PRAGMA table_info({t})").fetchall()
                    cnt  = conn.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
                    print(f"  {t:<30} cols={len(cols):>2}  rows={cnt}")
                conn.close()
            except Exception as e:
                print(f"  ERROR reading {rel}: {e}")
