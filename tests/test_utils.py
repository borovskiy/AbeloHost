from app.services.utils.utils_pandas_frame import get_user_id_for_n_countries
from app.schemas.report_schema import CountryStatsFilter


def test_get_user_id_for_n_countries():
    csv_str = "user_id;country\n1;Russia\n2;USA\n3;Russia\n"
    filters = CountryStatsFilter(sort_by="count", top_n=10)

    result = get_user_id_for_n_countries(countries_csv=csv_str, filters=filters)

    assert len(result.list_id_for_search) == 3
    assert len(result.list_id_data_csv) == 2
    assert result.list_id_data_csv[0].country == "Russia"
    assert result.list_id_data_csv[1].country == "USA"
