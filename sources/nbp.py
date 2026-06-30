"""NBP data ingestion module.

This module provides functionality to:
- fetch data from the NBP API,
- transform it into pandas DataFrames,
- save results to Databricks Delta tables.

Supported data sources:
- gold prices,
- exchange rates (tables A, B, C).
"""

from typing import Literal

import pandas as pd
import requests


class NBPSource:
    """Base class for NBP API sources."""

    def __init__(self, table: Literal["A", "B", "C"] | None) -> None:
        """Initialize NBP source.

        Args:
            table: Exchange rates table identifier.
        """
        self.table = table

    def get_data(self) -> list[dict] | None:
        """Fetch data from the NBP API.

        Returns:
            Parsed JSON response.
        """
        headers = {"Accept": "application/json"}

        response = requests.get(self.url, headers=headers, timeout=30)
        response.raise_for_status()

        return response.json()

    def save_data_to_databricks(
        self,
        df: pd.DataFrame,
        catalog: str,
        schema: str,
        table_name: str,
        mode: Literal["overwrite", "append", "ignore", "error"] = "overwrite",
    ) -> None:
        """Save DataFrame to Databricks Delta table.

        Args:
            df: DataFrame to save.
            catalog: Databricks catalog name.
            schema: Databricks schema name.
            table_name: Target table name.
            mode: Save mode.
        """
        if df is None:
            print("No data to save")
            return

        full_table_name = f"{catalog}.{schema}.{table_name}"

        df.write.format("delta").mode(mode).saveAsTable(full_table_name)


class NBPHistorySource(NBPSource):
    """NBP historical exchange rates source."""

    BASE_URL = "https://api.nbp.pl/api/exchangerates/tables"

    def __init__(
        self,
        table: Literal["A", "B", "C"],
        start_date: str | None = None,
        end_date: str | None = None,
    ) -> None:
        """Initialize historical NBP source.

        Args:
            table: Exchange rates table.
            start_date: Start date in YYYY-MM-DD format.
            end_date: End date in YYYY-MM-DD format.
        """
        super().__init__(table)

        if start_date and end_date:
            self.url = (
                f"{self.BASE_URL}/{self.table}/{start_date}/{end_date}/"
            )
        elif start_date:
            self.url = f"{self.BASE_URL}/{self.table}/{start_date}/"
        else:
            self.url = f"{self.BASE_URL}/{self.table}/today/"

    def transform_data_to_df(
        self,
        data: list[dict],
    ) -> pd.DataFrame:
        """Transform API response into DataFrame.

        Args:
            data: Raw API response.

        Returns:
            Pandas DataFrame with exchange rates.
        """
        if data is None:
            raise ValueError("No data to transform")

        rows = []

        for table in data:
            rows.append(table)

        return pd.DataFrame(rows)


class NBPGold(NBPSource):
    """NBP gold prices source."""

    BASE_URL = "https://api.nbp.pl/api/cenyzlota"

    def __init__(
        self,
        start_date: str | None = None,
        end_date: str | None = None,
    ) -> None:
        """Initialize gold prices source.

        Args:
            start_date: Start date in YYYY-MM-DD format.
            end_date: End date in YYYY-MM-DD format.
        """
        super().__init__(table=None)

        if start_date is None and end_date is None:
            self.url = f"{self.BASE_URL}/"
        elif start_date and end_date is None:
            self.url = f"{self.BASE_URL}/{start_date}/"
        else:
            self.url = (
                f"{self.BASE_URL}/{start_date}/{end_date}/"
            )

    def transform_data_to_df(
        self,
        data: list[dict],
    ) -> pd.DataFrame:
        """Transform gold prices response into DataFrame.

        Args:
            data: Raw API response.

        Returns:
            Pandas DataFrame with gold prices.
        """
        if data is None:
            raise ValueError("No data to transform")

        return pd.DataFrame(
            [
                {
                    "date": item["data"],
                    "price": item["cena"],
                }
                for item in data
            ]
        )


class NBPCurrent(NBPSource):
    """NBP current exchange rates source."""

    def __init__(
        self,
        table: Literal["A", "B", "C"],
    ) -> None:
        """Initialize current exchange rates source.

        Args:
            table: Exchange rates table.
        """
        super().__init__(table)

        self.url = (
            f"https://api.nbp.pl/api/exchangerates/tables/{self.table}/"
        )

    def transform_data_to_df(
        self,
        data: list[dict],
    ) -> pd.DataFrame:
        """Transform API response into DataFrame.

        Args:
            data: Raw API response.

        Returns:
            Pandas DataFrame with current exchange rates.
        """
        if data is None:
            raise ValueError(
                "transform_data_to_df() requires non-None data"
            )

        rates = data[0]

        return pd.DataFrame(rates)
