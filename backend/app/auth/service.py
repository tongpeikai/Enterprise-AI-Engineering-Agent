import base64
import hashlib
import hmac
import json
import secrets
import sqlite3
import time
from pathlib import Path
from uuid import uuid4


class AuthError(ValueError):
    pass


class AuthService:
    def __init__(self, path: str | Path, signing_key: str) -> None:
        self.path = str(path)
        self.signing_key = signing_key.encode()
        with sqlite3.connect(self.path) as db:
            db.execute(
                "CREATE TABLE IF NOT EXISTS users "
                "(id TEXT PRIMARY KEY, email TEXT UNIQUE NOT NULL, "
                "password_hash TEXT NOT NULL, role TEXT NOT NULL, org_id TEXT NOT NULL)"
            )
            db.execute(
                "CREATE TABLE IF NOT EXISTS refresh_tokens "
                "(token_hash TEXT PRIMARY KEY, user_id TEXT NOT NULL, "
                "expires_at REAL NOT NULL, revoked INTEGER NOT NULL DEFAULT 0)"
            )
            db.execute(
                "CREATE TABLE IF NOT EXISTS login_attempts "
                "(email TEXT PRIMARY KEY, failures INTEGER NOT NULL, "
                "blocked_until REAL NOT NULL DEFAULT 0)"
            )
            db.execute(
                "CREATE TABLE IF NOT EXISTS projects "
                "(id TEXT PRIMARY KEY, org_id TEXT NOT NULL, name TEXT NOT NULL, "
                "repository TEXT NOT NULL)"
            )

    @staticmethod
    def _password_hash(password: str, salt: bytes | None = None) -> str:
        salt = salt or secrets.token_bytes(16)
        digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 210_000)
        return f"{salt.hex()}${digest.hex()}"

    def register(self, email: str, password: str, org_id: str) -> str:
        if len(password) < 12 or "@" not in email:
            raise AuthError("invalid registration data")
        user_id = secrets.token_hex(16)
        with sqlite3.connect(self.path) as db:
            try:
                db.execute(
                    "INSERT INTO users VALUES (?, ?, ?, ?, ?)",
                    (
                        user_id,
                        email.lower(),
                        self._password_hash(password),
                        "member",
                        org_id,
                    ),
                )
            except sqlite3.IntegrityError as exc:
                raise AuthError("email already registered") from exc
        return user_id

    def login(self, email: str, password: str) -> str:
        with sqlite3.connect(self.path) as db:
            row = db.execute(
                "SELECT id, password_hash, role, org_id FROM users WHERE email=?",
                (email.lower(),),
            ).fetchone()
        if row is None:
            raise AuthError("invalid credentials")
        salt, expected = row[1].split("$", 1)
        actual = self._password_hash(password, bytes.fromhex(salt)).split("$", 1)[1]
        if not hmac.compare_digest(actual, expected):
            raise AuthError("invalid credentials")
        access, _ = self._issue_tokens({"sub": row[0], "role": row[2], "org": row[3]})
        return access

    def login_with_refresh(self, email: str, password: str) -> tuple[str, str]:
        normalized = email.lower()
        with sqlite3.connect(self.path) as db:
            attempt = db.execute(
                "SELECT failures, blocked_until FROM login_attempts WHERE email=?",
                (normalized,),
            ).fetchone()
            if attempt and attempt[1] > time.time():
                raise AuthError("temporarily blocked")
            row = db.execute(
                "SELECT id, password_hash, role, org_id FROM users WHERE email=?",
                (normalized,),
            ).fetchone()
        if row is None:
            self._record_login_failure(normalized)
            raise AuthError("invalid credentials")
        salt, expected = row[1].split("$", 1)
        actual = self._password_hash(password, bytes.fromhex(salt)).split("$", 1)[1]
        if not hmac.compare_digest(actual, expected):
            self._record_login_failure(normalized)
            raise AuthError("invalid credentials")
        with sqlite3.connect(self.path) as db:
            db.execute("DELETE FROM login_attempts WHERE email=?", (normalized,))
        return self._issue_tokens({"sub": row[0], "role": row[2], "org": row[3]})

    def _record_login_failure(self, email: str) -> None:
        with sqlite3.connect(self.path) as db:
            row = db.execute(
                "SELECT failures FROM login_attempts WHERE email=?", (email,)
            ).fetchone()
            failures = (row[0] if row else 0) + 1
            blocked_until = time.time() + 300 if failures >= 5 else 0
            db.execute(
                "INSERT OR REPLACE INTO login_attempts VALUES (?, ?, ?)",
                (email, failures, blocked_until),
            )

    def _issue_tokens(self, claims: dict[str, str]) -> tuple[str, str]:
        access = self._token(claims)
        refresh = secrets.token_urlsafe(32)
        with sqlite3.connect(self.path) as db:
            db.execute(
                "INSERT INTO refresh_tokens VALUES (?, ?, ?, 0)",
                (self._hash_token(refresh), claims["sub"], time.time() + 30 * 86400),
            )
        return access, refresh

    def refresh(self, refresh_token: str) -> tuple[str, str]:
        token_hash = self._hash_token(refresh_token)
        with sqlite3.connect(self.path) as db:
            row = db.execute(
                "SELECT user_id FROM refresh_tokens WHERE token_hash=? "
                "AND revoked=0 AND expires_at>?",
                (token_hash, time.time()),
            ).fetchone()
            if row is None:
                raise AuthError("invalid refresh token")
            db.execute(
                "UPDATE refresh_tokens SET revoked=1 WHERE token_hash=?", (token_hash,)
            )
            user = db.execute(
                "SELECT id, role, org_id FROM users WHERE id=?", (row[0],)
            ).fetchone()
        if user is None:
            raise AuthError("invalid refresh token")
        return self._issue_tokens({"sub": user[0], "role": user[1], "org": user[2]})

    def revoke(self, refresh_token: str) -> None:
        with sqlite3.connect(self.path) as db:
            db.execute(
                "UPDATE refresh_tokens SET revoked=1 WHERE token_hash=?",
                (self._hash_token(refresh_token),),
            )

    @staticmethod
    def _hash_token(token: str) -> str:
        return hashlib.sha256(token.encode()).hexdigest()

    def create_project(self, claims: dict[str, str], name: str, repository: str) -> str:
        project_id = str(uuid4())
        with sqlite3.connect(self.path) as db:
            db.execute(
                "INSERT INTO projects VALUES (?, ?, ?, ?)",
                (project_id, claims["org"], name, repository),
            )
        return project_id

    def list_projects(self, claims: dict[str, str]) -> list[dict[str, str]]:
        with sqlite3.connect(self.path) as db:
            rows = db.execute(
                "SELECT id, name, repository FROM projects WHERE org_id=?",
                (claims["org"],),
            ).fetchall()
        return [{"id": row[0], "name": row[1], "repository": row[2]} for row in rows]

    def _token(self, claims: dict[str, str]) -> str:
        body = {**claims, "exp": int(time.time()) + 3600}
        encoded = self._encode(body)
        signature = hmac.new(
            self.signing_key, encoded.encode(), hashlib.sha256
        ).hexdigest()
        return f"{encoded}.{signature}"

    def verify(self, token: str) -> dict[str, str]:
        try:
            encoded, signature = token.split(".", 1)
            expected = hmac.new(
                self.signing_key, encoded.encode(), hashlib.sha256
            ).hexdigest()
            claims = json.loads(base64.urlsafe_b64decode(encoded + "=="))
        except (ValueError, json.JSONDecodeError, UnicodeDecodeError) as exc:
            raise AuthError("invalid token") from exc
        if (
            not hmac.compare_digest(signature, expected)
            or not isinstance(claims, dict)
            or claims.get("exp", 0) < time.time()
        ):
            raise AuthError("invalid token")
        return claims

    @staticmethod
    def _encode(claims: dict[str, str | int]) -> str:
        raw = json.dumps(claims, separators=(",", ":")).encode()
        return base64.urlsafe_b64encode(raw).decode().rstrip("=")


def require_role(claims: dict[str, str], *roles: str) -> None:
    if claims.get("role") not in roles:
        raise AuthError("insufficient permissions")
