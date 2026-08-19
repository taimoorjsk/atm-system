"""Small SQLite persistence layer for the ATM application."""

from __future__ import annotations

import hashlib
import hmac
import secrets
import sqlite3
from datetime import datetime
from pathlib import Path


DEFAULT_DATABASE_PATH = Path(__file__).resolve().parent / "data" / "atm.db"


class Database:
    """Owns SQLite connections and the queries used by the application."""

    def __init__(self, path: str | Path = DEFAULT_DATABASE_PATH):
        self.path = Path(path)
        if self.path != Path(":memory:"):
            self.path.parent.mkdir(parents=True, exist_ok=True)
        self.connection = sqlite3.connect(self.path)
        self.connection.row_factory = sqlite3.Row
        self.connection.execute("PRAGMA foreign_keys = ON")
        self.create_tables()

    def create_tables(self) -> None:
        self.connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS customers (
                customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                phone TEXT NOT NULL,
                email TEXT NOT NULL,
                address TEXT NOT NULL,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS accounts (
                account_number TEXT PRIMARY KEY,
                customer_id INTEGER NOT NULL,
                account_type TEXT NOT NULL CHECK(account_type IN ('Savings', 'Current')),
                balance REAL NOT NULL,
                status TEXT NOT NULL DEFAULT 'ACTIVE',
                created_at TEXT NOT NULL,
                FOREIGN KEY(customer_id) REFERENCES customers(customer_id)
            );

            CREATE TABLE IF NOT EXISTS cards (
                account_number TEXT PRIMARY KEY,
                pin_hash TEXT NOT NULL,
                pin_salt TEXT NOT NULL,
                failed_attempts INTEGER NOT NULL DEFAULT 0,
                is_blocked INTEGER NOT NULL DEFAULT 0,
                FOREIGN KEY(account_number) REFERENCES accounts(account_number)
            );

            CREATE TABLE IF NOT EXISTS transactions (
                transaction_id TEXT PRIMARY KEY,
                account_number TEXT NOT NULL,
                transaction_type TEXT NOT NULL,
                amount REAL NOT NULL CHECK(amount > 0),
                description TEXT NOT NULL DEFAULT '',
                related_account TEXT,
                timestamp TEXT NOT NULL,
                FOREIGN KEY(account_number) REFERENCES accounts(account_number)
            );
            """
        )
        self.connection.commit()

    def close(self) -> None:
        self.connection.close()

    def add_customer(self, name: str, phone: str, email: str, address: str) -> int:
        cursor = self.connection.execute(
            """
            INSERT INTO customers (name, phone, email, address, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (name, phone, email, address, datetime.now().isoformat(timespec="seconds")),
        )
        self.connection.commit()
        return int(cursor.lastrowid)

    def next_account_number(self) -> str:
        row = self.connection.execute(
            "SELECT account_number FROM accounts ORDER BY CAST(account_number AS INTEGER) DESC LIMIT 1"
        ).fetchone()
        next_number = max(int(row[0]) + 1 if row else 10_000_001, 10_000_001)
        return str(next_number)

    def has_accounts(self) -> bool:
        row = self.connection.execute("SELECT 1 FROM accounts LIMIT 1").fetchone()
        return row is not None

    def add_account(
        self, account_number: str, customer_id: int, account_type: str, balance: float, pin: str
    ) -> None:
        created_at = datetime.now().isoformat(timespec="seconds")
        salt = secrets.token_bytes(16)
        pin_hash = hash_pin(pin, salt)
        with self.connection:
            self.connection.execute(
                """
                INSERT INTO accounts
                    (account_number, customer_id, account_type, balance, created_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (account_number, customer_id, account_type, balance, created_at),
            )
            self.connection.execute(
                """
                INSERT INTO cards (account_number, pin_hash, pin_salt)
                VALUES (?, ?, ?)
                """,
                (account_number, pin_hash, salt.hex()),
            )

    def get_account(self, account_number: str) -> sqlite3.Row | None:
        return self.connection.execute(
            """
            SELECT a.*, c.name, c.phone, c.email, c.address, c.customer_id
            FROM accounts AS a
            JOIN customers AS c ON c.customer_id = a.customer_id
            WHERE a.account_number = ?
            """,
            (account_number,),
        ).fetchone()

    def update_balance(self, account_number: str, balance: float) -> None:
        self.connection.execute(
            "UPDATE accounts SET balance = ? WHERE account_number = ?",
            (balance, account_number),
        )
        self.connection.commit()

    def update_customer(self, customer_id: int, name: str, phone: str, email: str, address: str) -> None:
        self.connection.execute(
            """
            UPDATE customers SET name = ?, phone = ?, email = ?, address = ?
            WHERE customer_id = ?
            """,
            (name, phone, email, address, customer_id),
        )
        self.connection.commit()

    def update_account_status(self, account_number: str, status: str) -> None:
        self.connection.execute(
            "UPDATE accounts SET status = ? WHERE account_number = ?",
            (status, account_number),
        )
        self.connection.commit()

    def update_pin(self, account_number: str, pin: str) -> None:
        salt = secrets.token_bytes(16)
        self.connection.execute(
            """
            UPDATE cards SET pin_hash = ?, pin_salt = ?, failed_attempts = 0, is_blocked = 0
            WHERE account_number = ?
            """,
            (hash_pin(pin, salt), salt.hex(), account_number),
        )
        self.connection.commit()

    def register_failed_pin_attempt(self, account_number: str, max_attempts: int = 3) -> int:
        self.connection.execute(
            """
            UPDATE cards
            SET failed_attempts = failed_attempts + 1,
                is_blocked = CASE WHEN failed_attempts + 1 >= ? THEN 1 ELSE 0 END
            WHERE account_number = ?
            """,
            (max_attempts, account_number),
        )
        self.connection.commit()
        row = self.connection.execute(
            "SELECT failed_attempts FROM cards WHERE account_number = ?",
            (account_number,),
        ).fetchone()
        return int(row[0]) if row else 0

    def reset_pin_attempts(self, account_number: str) -> None:
        self.connection.execute(
            "UPDATE cards SET failed_attempts = 0 WHERE account_number = ?",
            (account_number,),
        )
        self.connection.commit()

    def is_blocked(self, account_number: str) -> bool:
        row = self.connection.execute(
            "SELECT is_blocked FROM cards WHERE account_number = ?",
            (account_number,),
        ).fetchone()
        return bool(row and row[0])

    def verify_pin(self, account_number: str, pin: str) -> bool:
        row = self.connection.execute(
            "SELECT pin_hash, pin_salt FROM cards WHERE account_number = ?",
            (account_number,),
        ).fetchone()
        return bool(row and hmac.compare_digest(hash_pin(pin, bytes.fromhex(row[1])), row[0]))

    def record_transaction(
        self,
        account_number: str,
        transaction_type: str,
        amount: float,
        description: str = "",
        related_account: str | None = None,
    ) -> str:
        transaction_id = f"TXN{secrets.token_hex(5).upper()}"
        self.connection.execute(
            """
            INSERT INTO transactions
                (transaction_id, account_number, transaction_type, amount, description, related_account, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                transaction_id,
                account_number,
                transaction_type,
                amount,
                description,
                related_account,
                datetime.now().isoformat(timespec="seconds"),
            ),
        )
        self.connection.commit()
        return transaction_id

    def get_transactions(self, account_number: str, limit: int | None = 5) -> list[sqlite3.Row]:
        query = """
            SELECT * FROM transactions
            WHERE account_number = ?
            ORDER BY timestamp DESC
        """
        parameters: tuple[object, ...] = (account_number,)
        if limit is not None:
            query += " LIMIT ?"
            parameters += (limit,)
        return list(self.connection.execute(query, parameters).fetchall())


def hash_pin(pin: str, salt: bytes) -> str:
    """Hash a PIN with a per-card salt using a standard-library KDF."""
    return hashlib.pbkdf2_hmac("sha256", pin.encode("utf-8"), salt, 120_000).hex()
