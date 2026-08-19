# ATM System — Persistent Banking Application

A beginner-friendly ATM and personal banking system built with Python OOP, SQLite, custom exceptions, and CustomTkinter.

The active application uses a persistent SQLite backend through `database.py` and `banking.py`. The original in-memory modules and GUI screens remain in the repository as learning references and for the optional legacy console mode.

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

### 3. Run the application

```bash
python main.py
```

### 4. First run

On the first run, choose **Create your first account**. Enter the requested profile details, account type, opening deposit, and a four-digit PIN. The system generates the account number automatically and stores only a salted PIN hash. Use the generated account number and PIN to sign in.

### 5. Persistent backend tests

```bash
python -m unittest discover -s tests -v
```

The first application start creates `data/atm.db` and its tables automatically. SQLite is part of Python's standard library, so no database server is required.

### 6. Console mode (legacy/reference)

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
├── main.py            # Launcher (persistent GUI by default)
├── database.py        # SQLite schema, parameterized queries, PIN hashing
├── banking.py         # Persistent account and transaction service
├── data/atm.db        # Created automatically at runtime
├── tests/test_banking.py # Persistent backend workflow tests
├── gui/
│   ├── persistent_app.py  # Active persistent CustomTkinter application
│   ├── app.py              # Original in-memory GUI reference
│   ├── data_setup.py       # Original dummy-data factory
│   ├── utils.py            # Original exception-to-popup helpers
│   └── screens/            # Original PIN, dashboard, and dialog screens
└── requirements.txt
```

## Features

### Persistent account management

- Create Savings or Current accounts.
- Automatically generate unique account numbers beginning at `10000001`.
- Store customer name, phone, email, address, account type, balance, status, and creation time.
- Edit profile information from the dashboard.
- Close an account using soft deletion: the record becomes `CLOSED` and transaction history remains available.
- Accounts with non-zero balances cannot be closed.

### Secure authentication

- Sign in with account number and four-digit PIN.
- PINs are hashed with PBKDF2-HMAC-SHA256 and a unique random salt.
- Plaintext PINs are not stored in SQLite.
- Three failed attempts permanently block the account until the PIN is reset.
- Closed and blocked accounts cannot sign in.
- Change PIN from the dashboard after verifying the current PIN.

### Banking operations

- Deposit positive amounts.
- Withdraw cash using available ATM denominations: Rs. 5,000, Rs. 1,000, and Rs. 500.
- Transfer money between two active accounts.
- Prevent transfers to the same account.
- Record both outgoing and incoming transfer history.
- Apply Savings minimum-balance and withdrawal-limit rules.
- Apply Current overdraft rules.
- Display transaction IDs and updated balances after successful operations.

### Premium GUI experience

- Dark neon banking theme with black, navy, blue, and cyan accents.
- Optional light mode with white surfaces, dark navy text, and neon blue accents.
- Theme toggle available on login and dashboard; switching rebuilds the current screen immediately.
- Interactive ATM card visual with mouse-based perspective tilt.
- Card displays the account holder name and account number.
- Scrollable account-creation form for smaller screens.
- Styled modal forms for deposit, withdrawal, transfers, profile updates, PIN changes, and account closure.
- Inline validation messages instead of repeated system input prompts.
- Enter-key support in amount, transfer, and PIN forms.
- Dismissible bottom-right banking safety tips on login and dashboard.
- Transaction activity panel showing recent account movements.

### Database tables

- `customers` stores profile details.
- `accounts` stores account type, balance, status, and creation time.
- `cards` stores a salted PBKDF2 PIN hash, salt, failed-attempt count, and blocked state, never the plaintext PIN.
- `transactions` stores immutable transaction records and related account numbers.

`BankService` is the boundary between the domain classes and SQLite. It validates input, loads the appropriate `SavingsAccount` or `CurrentAccount`, delegates business rules to that object, then persists the new balance and transaction record.

The database is initialized automatically when `Database()` is created. SQLite connections use `sqlite3.Row` for readable column access, foreign keys are enabled, and all values are passed through parameterized queries.

### OOP Principles in Practice

| Principle | Where |
|-----------|-------|
| **Encapsulation** | Private `__balance`, `__pin` in `Account`; `__pin`, `__failed_attempts` in `Card` |
| **Inheritance** | `SavingsAccount` / `CurrentAccount` extend abstract `Account` |
| **Abstraction** | `Account._validate_withdrawal()` and `Transaction.format_for_statement()` |
| **Polymorphism** | Savings enforces minimum balance; Current allows overdraft — same `withdraw()` call |

### Data Flow (Persistent GUI → Backend → SQLite)

```
User clicks "Withdraw"
    → Persistent GUI modal validates the amount
    → BankService.withdraw(account_number, amount)
        → Database loads the account
        → ATM checks cash notes
        → SavingsAccount or CurrentAccount validates the withdrawal
        → Database updates the balance
        → Database records the transaction
    → Receipt message and refreshed dashboard
```

---

## GUI Library Choice: CustomTkinter

| Library | Pros | Cons |
|---------|------|------|
| **CustomTkinter**  | Modern dark theme, zero licensing issues, pip install, great for demos | Less powerful than Qt for huge apps |
| PyQt6 / PySide6 | Very powerful, native widgets | Steeper learning curve, licensing considerations |
| Tkinter (plain) | Built-in | Looks dated |

**CustomTkinter** was chosen because it looks professional for an internship portfolio, installs in one command, and keeps the GUI layer thin without touching your backend.

---

## Active GUI Screens

1. **Login** — Account number and PIN authentication, first-run account creation, theme toggle, and safety tip.
2. **Create Account** — Scrollable profile, account type, opening deposit, and PIN form.
3. **Dashboard** — Greeting, interactive ATM card, available balance, account details, quick actions, theme toggle, logout, recent activity, and safety tip.
4. **Deposit / Withdraw** — Styled modal forms with amount validation and transaction receipts.
5. **Transfer** — Single form for destination account and amount with inline errors.
6. **Edit Profile** — Prefilled form for name, phone, email, and address.
7. **Change PIN** — Current PIN, new PIN, and confirmation fields.
8. **Close Account** — PIN confirmation and zero-balance check before soft closure.

The original PIN keypad, dashboard, and mini-statement screens remain in `gui/screens/` as a reference implementation for the earlier in-memory assignment.

---

## Business Rules (Backend)

- **Account creation**: names are required, email and phone have basic validation, Savings accounts require at least Rs. 5,000, and PINs must be exactly four digits.
- **Deposits**: amount must be greater than zero.
- **Withdrawals**: amount must be positive and a multiple of Rs. 500.
- **Savings**: minimum balance Rs. 5,000 and maximum withdrawal Rs. 50,000 per transaction.
- **Current**: overdraft limit Rs. 50,000.
- **Transfers**: destination must exist and be active; source and destination cannot be the same.
- **PIN security**: three failed attempts block the account.
- **Account status**: closed accounts cannot authenticate or perform operations.
- **ATM cash**: withdrawals use the available Rs. 5,000, Rs. 1,000, and Rs. 500 notes.

---

## Exception Handling

The backend raises typed custom exceptions such as `InvalidPINError`, `CardBlockedError`, `InsufficientBalanceError`, `InvalidAmountError`, `AccountNotFoundError`, `AccountClosedError`, and `InsufficientATMFundsError`. The persistent GUI catches these exceptions and displays friendly inline messages or dialogs instead of showing tracebacks.

The original GUI also demonstrates centralized exception-to-popup mapping:

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

## Manual Testing Guide

1. Start with a new database, select **Create your first account**, and create a Current account with a four-digit PIN.
2. Confirm the generated account number appears in the sign-in field and log in.
3. Switch between **LIGHT MODE** and **DARK MODE** on the dashboard. Confirm cards, labels, dialogs, history, and tips update.
4. Hover over the ATM card and move the mouse around it. Confirm the card tilts and displays the correct name and account number.
5. Deposit a positive amount and confirm the balance, receipt, and transaction activity update.
6. Try a zero, negative, or non-numeric deposit and confirm an inline validation message appears.
7. Withdraw a supported amount and confirm the receipt and balance update. Try an unsupported denomination or insufficient balance.
8. Create a second account, transfer money to it, and confirm both account histories are recorded.
9. Edit the profile and confirm the dashboard greeting updates.
10. Change the PIN, log out, and authenticate with the new PIN.
11. Enter a wrong PIN three times and confirm the account becomes blocked.
12. Attempt to close an account with a non-zero balance and confirm closure is rejected.
13. Empty an account, close it, and confirm the account is marked closed while its transaction history remains in SQLite.
14. Dismiss the bottom-right banking tip with the `×` button on both login and dashboard.

## Automated Tests

Run:

```bash
python -m unittest discover -s tests -v
```

Automated coverage currently includes account creation, duplicate account number sequencing, salted PIN verification, three-attempt lockout, deposits, withdrawals, transfers, transaction history, invalid amounts, profile/PIN workflows, and soft account closure.

## Important Concepts To Explain

- Object-oriented encapsulation, inheritance, abstraction, and polymorphism.
- Service-layer separation between GUI, business rules, and persistence.
- SQLite CRUD operations and parameterized SQL.
- Password/PIN hashing with a salt and PBKDF2.
- Account state transitions: active, blocked, and closed.
- Transaction recording and double-entry transfer history.
- Input validation and typed exception handling.
- CustomTkinter layout, reusable widgets, modal dialogs, and theme palettes.
- Canvas drawing and mouse-event handling for the interactive card.

## Future Improvements

- Persist ATM cash inventory in its own database table.
- Add transaction filtering and full statement export.
- Add receipt export to `.txt` files.
- Add a dedicated ATM status and cash inventory panel.
- Add password/PIN recovery through a controlled administrator workflow.
- Add more isolated unit tests for ATM denomination combinations and daily limits.

---

## Author
M. Taimoor Jahangir
Python Backend Engineering Intern — Enigmatix
