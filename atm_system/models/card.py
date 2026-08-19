from atm_system.config import CARD_MAX_PIN_ATTEMPTS
from atm_system.exceptions import CardBlockedError, InvalidPINError


class Card:
    def __init__(self, card_number: str, pin: str):
        self.card_number = card_number
        self.__pin = pin
        self.__is_blocked = False
        self.__failed_attempts = 0

    def is_blocked(self) -> bool:
        return self.__is_blocked

    def masked_number(self) -> str:
        return f"**** **** **** {self.card_number[-4:]}"

    def validate_pin(self, entered_pin: str) -> bool:
        if self.__is_blocked:
            raise CardBlockedError()

        if entered_pin == self.__pin:
            self.__failed_attempts = 0
            return True

        self.__failed_attempts += 1
        if self.__failed_attempts >= CARD_MAX_PIN_ATTEMPTS:
            self.__is_blocked = True
            raise CardBlockedError("Maximum attempts reached. Card is now blocked.")

        remaining = CARD_MAX_PIN_ATTEMPTS - self.__failed_attempts
        raise InvalidPINError(f"Invalid PIN. Attempts remaining: {remaining}")

    def change_pin(self, old_pin: str, new_pin: str) -> bool:
        if self.validate_pin(old_pin):
            self.__pin = new_pin
            return True
        return False
