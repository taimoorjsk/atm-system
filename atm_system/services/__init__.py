from dataclasses import dataclass, field
from datetime import datetime

from atm_system.models.transaction import Transaction


@dataclass
class AuditEntry:
    timestamp: datetime
    event: str
    detail: str
    customer_id: str | None = None


class AuditLog:
    def __init__(self):
        self._entries: list[AuditEntry] = []

    def record(self, event: str, detail: str, customer_id: str | None = None) -> None:
        self._entries.append(AuditEntry(datetime.now(), event, detail, customer_id))

    def recent(self, limit: int = 50) -> list[AuditEntry]:
        return list(reversed(self._entries[-limit:]))

    def format_log(self, limit: int = 30) -> str:
        lines = ["=" * 52, "ATM AUDIT LOG", "=" * 52]
        for entry in self.recent(limit):
            ts = entry.timestamp.strftime("%d-%b %H:%M:%S")
            cid = entry.customer_id or "—"
            lines.append(f"[{ts}] ({cid}) {entry.event}: {entry.detail}")
        if not self._entries:
            lines.append("No activity recorded yet.")
        return "\n".join(lines)


@dataclass
class TransactionResult:
    transaction: Transaction
    message: str
    new_balance: float
    notes_dispensed: dict[int, int] = field(default_factory=dict)
