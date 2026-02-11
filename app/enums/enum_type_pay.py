from enum import Enum


class PayEnum:
    PAYMENT = "payment"
    INVOICE = "invoice"
    ALL = "all"


class TypePayEnum(str, Enum):
    PAYMENT = PayEnum.PAYMENT
    INVOICE = PayEnum.INVOICE


class APITypePayEnum(str, Enum):
    PAYMENT = PayEnum.PAYMENT
    INVOICE = PayEnum.INVOICE
    ALL = PayEnum.ALL
