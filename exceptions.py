# exceptions.py

class InvalidPINError(Exception):
    def __init__(self, message="Invalid PIN entered."):
        super().__init__(message)

class CardBlockedError(Exception):
    def __init__(self, message="This card has been blocked due to multiple incorrect attempts."):
        super().__init__(message)

class InsufficientBalanceError(Exception):
    def __init__(self, message="Insufficient account balance for this transaction."):
        super().__init__(message)

class InsufficientATMFundsError(Exception):
    def __init__(self, message="ATM has insufficient cash to dispense this amount."):
        super().__init__(message)

class InvalidAmountError(Exception):
    def __init__(self, message="The requested amount is invalid (must be greater than zero)."):
        super().__init__(message)

class AccountInactiveError(Exception):
    def __init__(self, message="This account is currently inactive and blocked from transactions."):
        super().__init__(message)

class DailyLimitExceededError(Exception):
    def __init__(self, message="The daily transaction limit has been exceeded."):
        super().__init__(message)

class InvalidAccountError(Exception):
    def __init__(self, message="The specified account does not exist or is invalid."):
        super().__init__(message)

class AccountNotFoundError(Exception):
    def __init__(self, message="The specified account could not be found."):
        super().__init__(message)

class AccountClosedError(Exception):
    def __init__(self, message="This account is closed and cannot be used."):
        super().__init__(message)