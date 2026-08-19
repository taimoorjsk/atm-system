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
    def __init__(self, message="The requested amount is invalid."):
        super().__init__(message)


class AccountInactiveError(Exception):
    def __init__(self, message="This account is currently inactive."):
        super().__init__(message)


class DailyLimitExceededError(Exception):
    def __init__(self, message="Daily withdrawal limit exceeded."):
        super().__init__(message)


class InvalidAccountError(Exception):
    def __init__(self, message="The specified account does not exist."):
        super().__init__(message)


class BillPaymentError(Exception):
    def __init__(self, message="Bill payment could not be processed."):
        super().__init__(message)


class FixedDepositLockError(Exception):
    def __init__(self, message="Fixed deposit is still in lock-in period."):
        super().__init__(message)
