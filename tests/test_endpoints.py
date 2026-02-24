from unittest.mock import patch, AsyncMock


def test_get_report(client):
    with patch(
        "app.services.report_service.ReportServices.get_all_report_by_filter"
    ) as mock_method:
        mock_method.return_value = AsyncMock()
        mock_method.return_value = {
            "total_amount": 999.99,
            "transaction_count": 1,
            "avg_amount": 999.99,
            "min_amount": 999.99,
            "max_amount": 999.99,
            "daily_shifts": None,
        }

        response = client.get("/api/v1/reports/report")
        assert response.status_code == 200
        data = response.json()
        assert data["total_amount"] == 999.99


def test_get_country_stats_success(client):
    csv_content = "user_id;country\n1;Russia\n2;USA\n"
    from io import BytesIO

    file = ("countries.csv", BytesIO(csv_content.encode()), "text/csv")

    with patch(
        "app.services.report_service.ReportServices.get_report_country"
    ) as mock_method:
        mock_method.return_value = AsyncMock()
        mock_method.return_value = [
            {
                "country": "Russia",
                "transaction_count": 1,
                "total_amount": 100.0,
                "average_amount": 100.0,
            }
        ]

        response = client.post(
            "/api/v1/reports/report/by-country",
            files={"countries_file": file},
            data={"sort_by": "count", "top_n": 10},
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["country"] == "Russia"


def test_get_country_stats_bad_file(client):
    file = ("bad_file.txt", b"not a csv", "text/plain")
    response = client.post(
        "/api/v1/reports/report/by-country",
        files={"countries_file": file},
        data={"sort_by": "count"},
    )
    assert response.status_code == 400
