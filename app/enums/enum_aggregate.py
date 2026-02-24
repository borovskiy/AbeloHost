from enum import Enum


class TransactionFieldEnum(Enum):
    TOTAL_AMOUNT = "total_amount"
    TRANSACTION_COUNT = "transaction_count"
    AVG_AMOUNT = "avg_amount"
    MIN_AMOUNT = "min_amount"
    MAX_AMOUNT = "max_amount"
    DAY_DATE = "day_date"
    DAILY_TOTAL = "daily_total"
    DAILY_COUNT = "daily_count"
    DAILY_PAY = "date_pay"
    DAY = "day"
    SUM_PAY = "sum_pay"
    DAILY_TOTALS = "daily_totals"
    PREV_DAY_TOTAL = "prev_day_total"
    PERCENTAGE_CHANGE = "percentage_change"
    FILTERED_TRANSACTION = "filtered_transactions"
