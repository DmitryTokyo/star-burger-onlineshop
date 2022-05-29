from enum import Enum


class OrderStatus(Enum):
    incomplete = 'необработанный'
    complete = 'обработанный'


class PaymentMethod(Enum):
    cash = 'cash'
    card = 'card'
