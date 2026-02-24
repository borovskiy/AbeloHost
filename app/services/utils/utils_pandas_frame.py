from io import StringIO

import pandas as pd
from pandas import DataFrame

from app.schemas.report_schema import CountryStatsFilter, CSVDataList, CSVData


def check_column_in_csv(set_column: set, frame: DataFrame):
    if not set_column.issubset(frame.columns):
        missing = set_column - set(frame.columns)
        raise ValueError(f"Отсутствуют обязательные колонки в CSV: {missing}")


def read_frame(countries_csv: str, sep: str):
    try:
        countries_df = pd.read_csv(StringIO(countries_csv), sep=sep)
    except Exception as e:
        raise ValueError(f"Ошибка парсинга CSV: {str(e)}")
    return countries_df


def get_user_id_for_n_countries(
    countries_csv: str, filters: CountryStatsFilter
) -> CSVDataList:
    countries_df = read_frame(countries_csv, ";")
    check_column_in_csv({"user_id", "country"}, countries_df)
    grouped = countries_df.groupby("country")["user_id"].apply(list).to_dict()
    # Сортируем страны по количеству пользователей (по убыванию)
    sorted_countries = sorted(grouped.items(), key=lambda x: len(x[0]), reverse=True)
    # Ограничиваем top_n, если задано
    selected_countries = (
        sorted_countries[: filters.top_n] if filters.top_n else sorted_countries
    )
    data_obj = CSVDataList()
    for country_name, user_ids in selected_countries:
        data_obj.list_for_frame_user_country.extend(
            [{"user_id": id_user, "country": country_name} for id_user in user_ids]
        )
        data_obj.list_id_for_search.extend(user_ids)
        data_obj.list_id_data_csv.append(
            CSVData(country=country_name, list_id_user_country=user_ids.copy())
        )
    return data_obj
