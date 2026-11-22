# -*- coding: utf-8 -*-
"""Single-use sign-in links (2026-11-21).

Accounts are a username and a password, with no email on file, so a friend who
forgets their password has no way back in. Aaron runs make_login_link.py on
his laptop, sends the printed link over chat, and the friend taps it.

- The token is `secrets.token_urlsafe(32)`. Only its SHA-256 is stored, so the
  table (or a backup of it) can't sign anyone in.
- A link lasts LINK_LIFETIME and works once. Making a new link for a user
  revokes that user's earlier unused links.
- Opening the link (GET) changes nothing: chat apps fetch links to build
  previews, and a GET that spent the token would kill it before the friend
  tapped it. The page's button POSTs, and only that spends it (redeem_link).
- Every reader returns None when the login_links table doesn't exist yet, so
  the code can deploy before the Neon migration (migrate_login_links_2026_11.py).

Timestamps are naive UTC written from Python, never from the database clock:
on Neon a TIMESTAMP default follows the session time zone, and on SQLite they
are 'YYYY-MM-DD HH:MM:SS' text, which compares correctly as long as every row
uses that one shape.
"""

import hashlib
import re
import secrets
from datetime import datetime, timedelta, timezone

import database

LINK_LIFETIME = timedelta(days=7)
TOKEN_BYTES = 32  # token_urlsafe(32) is 43 characters

# Anything else in the URL is refused before it reaches the database.
_TOKEN_RE = re.compile(r"[A-Za-z0-9_-]{20,128}")


def new_token():
    return secrets.token_urlsafe(TOKEN_BYTES)


def hash_token(token):
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def looks_like_token(token):
    return isinstance(token, str) and bool(_TOKEN_RE.fullmatch(token))


def utc_now():
    return datetime.now(timezone.utc).replace(tzinfo=None, microsecond=0)


def _ts(dt):
    """Postgres takes the datetime; SQLite gets CURRENT_TIMESTAMP's text shape."""
    return dt if database._is_postgres() else dt.strftime("%Y-%m-%d %H:%M:%S")


def table_exists(conn):
    if database._is_postgres():
        row = conn.execute("SELECT to_regclass('public.login_links') AS t").fetchone()
        return row is not None and row["t"] is not None
    row = conn.execute(
        "SELECT name FROM sqlite_master WHERE type = 'table' AND name = 'login_links'"
    ).fetchone()
    return row is not None


def create_link(user_id, lifetime=LINK_LIFETIME):
    """Store a new link for user_id. Returns (token, expires_at, revoked), where
    revoked counts this user's earlier unused links that were switched off.
    Raises if the table is missing: the CLI checks table_exists() first."""
    token = new_token()
    now = utc_now()
    expires_at = now + lifetime
    conn = database.get_db()
    try:
        cur = conn.execute(
            "UPDATE login_links SET expires_at = ? "
            "WHERE user_id = ? AND used_at IS NULL AND expires_at > ?",
            (_ts(now), user_id, _ts(now)),
        )
        revoked = max(cur.rowcount, 0)
        conn.execute(
            "INSERT INTO login_links (token_hash, user_id, created_at, expires_at) "
            "VALUES (?, ?, ?, ?)",
            (hash_token(token), user_id, _ts(now), _ts(expires_at)),
        )
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
    return token, expires_at, revoked


_USER_FOR_LINK = (
    "SELECT u.id, u.username FROM login_links l "
    "JOIN users u ON u.id = l.user_id WHERE l.token_hash = ?"
)


def peek_link(token):
    """The (id, username) row a live link belongs to, or None. Spends nothing."""
    if not looks_like_token(token):
        return None
    conn = database.get_db()
    try:
        return conn.execute(
            _USER_FOR_LINK + " AND l.used_at IS NULL AND l.expires_at > ?",
            (hash_token(token), _ts(utc_now())),
        ).fetchone()
    except database._operational_errors():
        conn.rollback()  # Postgres aborts the transaction on a missing table
        return None
    finally:
        conn.close()


def redeem_link(token):
    """Spend a live link and return its (id, username) row, or None.

    The UPDATE's WHERE clause is the single-use check, so two taps racing each
    other can't both get in: only one of them updates a row."""
    if not looks_like_token(token):
        return None
    token_hash = hash_token(token)
    now = _ts(utc_now())
    conn = database.get_db()
    try:
        cur = conn.execute(
            "UPDATE login_links SET used_at = ? "
            "WHERE token_hash = ? AND used_at IS NULL AND expires_at > ?",
            (now, token_hash, now),
        )
        user = conn.execute(_USER_FOR_LINK, (token_hash,)).fetchone() if cur.rowcount == 1 else None
        if user is None:
            conn.rollback()
            return None
        conn.commit()
        return user
    except database._operational_errors():
        conn.rollback()
        return None
    finally:
        conn.close()
