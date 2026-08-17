# ATM System — Class-Based OOP (Enigmatix Assignment)

A fully decoupled ATM backend built with Python OOP principles, now with a modern **CustomTkinter** GUI.

---

## Quick Start

### 1. Prerequisites

- Python **3.10+** (tested on 3.11)
- pip

### 2. Install dependencies

```bash
cd atm-system
pip install -r requirements.txt
```

### 3. Run the GUI

```bash
python main.py
```

Or directly:

```bash
python -m gui.app
```

### 4. Demo credentials

| Item | Value |
|------|-------|
| **PIN** | `1234` |
| **Savings Account** | `1001` — Rs. 25,000 |
| **Current Account** | `2001` — Rs. 10,000 |

### 5. Console mode (optional)

The original text interface is still available:

```bash
python main.py --console
```

---

## Project Architecture

```
atm-system/
├── exceptions.py      # Custom business-logic errors
├── entities.py        # Card & Customer
├── accounts.py        # Abstract Account + Savings/Current subclasses
├── transactions.py    # Transaction hierarchy (Deposit, Withdraw, Transfer)
├── atm.py             # ATM controller (cash dispensing, transaction processing)
├── main.py            # Launcher (GUI by default, --console for text mode)
├── gui/               # Graphical interface (does NOT modify backend)
│   ├── app.py         # Main window & screen navigation
│   ├── data_setup.py  # Dummy data factory
│   ├── utils.py       # Exception → popup mapping
│   └── screens/
│       ├── pin_screen.py    # PIN keypad + 3-attempt lockout
│       ├── dashboard.py     # Balances + transaction menu
│       └── dialogs.py       # Deposit, Withdraw, Transfer, PIN, Statement
└── requirements.txt
```

### OOP Principles in Practice

| Principle | Where |
|-----------|-------|
| **Encapsulation** | Private `__balance`, `__pin` in `Account`; `__pin`, `__failed_attempts` in `Card` |
| **Inheritance** | `SavingsAccount` / `CurrentAccount` extend abstract `Account` |
| **Abstraction** | `Account._validate_withdrawal()` and `Transaction.format_for_statement()` |
| **Polymorphism** | Savings enforces minimum balance; Current allows overdraft — same `withdraw()` call |

### Data Flow (GUI → Backend)

```
User clicks "Withdraw"
    → WithdrawDialog collects amount
    → atm.process_withdrawal(account, amount)
        → ATM checks cash notes (greedy algorithm)
        → account.withdraw(amount)  ← polymorphic validation
        → WithdrawalTransaction logged
    → Success popup OR custom exception caught → error popup
```

---

## GUI Library Choice: CustomTkinter

| Library | Pros | Cons |
|---------|------|------|
| **CustomTkinter** ✅ | Modern dark theme, zero licensing issues, pip install, great for demos | Less powerful than Qt for huge apps |
| PyQt6 / PySide6 | Very powerful, native widgets | Steeper learning curve, licensing considerations |
| Tkinter (plain) | Built-in | Looks dated |

**CustomTkinter** was chosen because it looks professional for an internship portfolio, installs in one command, and keeps the GUI layer thin without touching your backend.

---

## GUI Screens

1. **PIN Screen** — Numeric keypad, masks input, catches `InvalidPINError` and `CardBlockedError`
2. **Dashboard** — Shows all accounts, live balances, ATM cash inventory
3. **Deposit / Withdraw / Transfer** — Modal dialogs with validation
4. **Change PIN** — Syncs card + account PIN
5. **Mini Statement** — Last 5 transactions in monospace view

---

## Business Rules (Backend)

- **Withdrawals** must be multiples of **Rs. 500**
- **Savings**: min balance Rs. 5,000; max withdrawal Rs. 50,000 per transaction
- **Current**: overdraft limit Rs. 50,000
- **PIN**: 3 wrong attempts → card blocked (`CardBlockedError`)
- **ATM cash**: greedy note dispensing (5000 / 1000 / 500 denominations)

---

## How Exception Handling Works in the GUI

Backend raises typed exceptions; the GUI never parses error strings:

```python
# gui/utils.py
def handle_transaction_error(exc: Exception) -> None:
    if isinstance(exc, InvalidPINError):
        show_error("Invalid PIN", str(exc))
    elif isinstance(exc, CardBlockedError):
        show_error("Card Blocked", str(exc))
    # ... etc.
```

PIN screen example:

```python
try:
    if self.customer.card.validate_pin(self._pin_buffer):
        self.on_success()
except InvalidPINError as exc:
    show_error("Invalid PIN", str(exc))
except CardBlockedError as exc:
    show_error("Card Blocked", str(exc))
    self.after(500, lambda: self.master.winfo_toplevel().destroy())
```

---

## Testing Scenarios

Try these to verify the system:

1. Enter wrong PIN twice → see "Attempts remaining: 1"
2. Third wrong PIN → card blocked, app closes
3. Withdraw Rs. 24,000 from Savings → fails (min balance Rs. 5,000)
4. Transfer Rs. 2,000 from `1001` → `2001` → both balances update
5. Withdraw Rs. 1,500 → fails (not multiple of 500)
6. Run a few transactions, then open Mini Statement

---

## Author
M. Taimoor Jahangir
Python Backend Engineering Intern — Enigmatix
