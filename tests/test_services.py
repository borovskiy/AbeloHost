import pytest
from decimal import Decimal
from unittest.mock import AsyncMock


@pytest.mark.asyncio
async def test_get_report_country(mock_report_service):
    # Подготовим транзакции
    mock_trans = [
        type("obj", (), {"user_id": 1, "sum_pay": Decimal("100.00")}),
        type("obj", (), {"user_id": 2, "sum_pay": Decimal("200.00")}),
    ]
    mock_report_service.report_repo.get_trans_user_ids.return_value = mock_trans

    # CSV данные
    csv_str = "user_id;country\n1;Russia\n2;USA\n"
    from app.schemas.report_schema import CountryStatsFilter

    filters = CountryStatsFilter(sort_by="total", top_n=10)

    result = await mock_report_service.get_report_country(
        countries_csv=csv_str, filters=filters
    )

    assert len(result) == 2
    assert result[0].country == "Russia"
    assert result[0].total_amount == 100.0
    assert result[1].country == "USA"
    assert result[1].total_amount == 200.0
