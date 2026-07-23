"""Daily database backup, run by a PythonAnywhere scheduled task.

Uses SQLite's online-backup API instead of a plain file copy, so the backup
is consistent even if someone is using the app mid-backup (a raw `cp` can
capture a half-written transaction; this can't).

Keeps the last 7 daily backups in ~/backups and deletes older ones.

Scheduled task command:
    /home/sepulturian/bomu/venv/bin/python /home/sepulturian/bomu/backup_db.py
"""

import datetime
import glob
import os
import sqlite3

DB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bomu.db")
BACKUP_DIR = os.path.expanduser("~/backups")
KEEP = 7


def main():
    os.makedirs(BACKUP_DIR, exist_ok=True)
    stamp = datetime.date.today().isoformat()
    dest_path = os.path.join(BACKUP_DIR, f"bomu-{stamp}.db")

    src = sqlite3.connect(DB)
    dest = sqlite3.connect(dest_path)
    with dest:
        src.backup(dest)  # consistent snapshot, safe while app is live
    dest.close()
    src.close()

    # Sanity: the backup must open and pass an integrity check, otherwise
    # we'd happily rotate good backups away in favour of broken ones.
    check = sqlite3.connect(dest_path)
    ok = check.execute("PRAGMA integrity_check").fetchone()[0]
    check.close()
    if ok != "ok":
        os.remove(dest_path)
        raise SystemExit(f"Backup FAILED integrity check ({ok}); removed {dest_path}")

    # Rotate: newest first, delete everything past KEEP
    backups = sorted(glob.glob(os.path.join(BACKUP_DIR, "bomu-*.db")), reverse=True)
    for old in backups[KEEP:]:
        os.remove(old)

    print(f"Backed up to {dest_path} ({os.path.getsize(dest_path)} bytes), "
          f"{min(len(backups), KEEP)} backups kept.")


if __name__ == "__main__":
    main()
