from unittest.mock import AsyncMock

import pytest
from decimal import Decimal
from app.models import TransactionModel


@pytest.mark.asyncio
async def test_get_trans_user_ids(mock_transaction_repo):
    fake_transactions = [
        TransactionModel(user_id=1, sum_pay=Decimal("100.00")),
        TransactionModel(user_id=2, sum_pay=Decimal("200.00"))
    ]

    # Перезаписываем мок, установленный в фикстуре
    mock_transaction_repo.get_trans_user_ids.return_value = fake_transactions

    result = await mock_transaction_repo.get_trans_user_ids([1, 2])

    assert len(result) == 2
    assert result[0].user_id == 1
    assert result[1].user_id == 2