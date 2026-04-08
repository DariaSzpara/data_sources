"""NBP data ingestion module.

This module provides functionality to:
- fetch data from the NBP API,
- transform it into pandas DataFrames,
- save results to Databricks Delta tables.

Supported data sources:
- gold prices,
- exchange rates (tables A, B, C).
"""
from enum import Enum
from http import HTTPStatus
from typing import Literal

import pandas as pd
import requests


class SourceType(Enum):
    """Enumeration of supported data sources from NBP API.

    Attributes:
        GOLD: Gold prices endpoint.
        EXCHANGE_RATES: Exchange rates endpoint.
    """
    GOLD = "GOLD"
    EXCHANGE_RATES = "EXCHANGE_RATES"

class NBPSource:
    """Client for fetching and processing data from the NBP API.

    Depending on the selected source type, this class:
    - builds the appropriate API URL,
    - fetches data,
    - transforms it into a pandas DataFrame,
    - saves it to Databricks.

    Attributes:
        table (Literal["A", "B", "C"]):
        Exchange rate table type (only for EXCHANGE_RATES).
        source_type (SourceType): Type of data source.
        url (str): API endpoint URL.
    """
    def __init__(self, table:Literal["A","B","C"], source_type:SourceType):
        """Initialize NBP data source configuration.

        Args:
            table: Exchange rate table identifier ("A", "B", or "C").
            source_type: Type of data source (e.g., GOLD or EXCHANGE_RATES).

        Raises:
            ValueError: If unsupported source_type is provided.
        """
        self.table = table
        self.source_type = source_type
        if self.source_type is SourceType.GOLD.value:
            self.url = "https://api.nbp.pl/api/cenyzlota"
        elif self.source_type is SourceType.EXCHANGE_RATES.value:
            self.url = f"http://api.nbp.pl/api/exchangerates/tables/{self.table}/"
        else:
            raise ValueError(f"Source type {source_type} is not supported")
    def get_data(self)-> list[dict] | None:
        """Fetch data from the NBP API.

        Sends a GET request to the configured endpoint and returns parsed JSON.

        Returns:
            Parsed JSON response as Python object (dict/list) if successful,
            otherwise None.
        """
        headers = {
            "Accept": "application/json"
            }
        response = requests.get(self.url,headers=headers)
        if response.status_code == HTTPStatus.OK:
            return response.json()
        print(f"Error: {response.status_code}")
        return None
    def transform_data_to_df(self,data: list[dict] | None) -> pd.DataFrame | None:
        """Transform raw API data into a pandas DataFrame.

        The transformation depends on the selected source type:
        - GOLD: Converts full response directly into DataFrame.
        - EXCHANGE_RATES: Extracts "rates" field before conversion.

        Args:
            data: Raw JSON data returned from the API.

        Returns:
            pandas DataFrame with transformed data, or None if input is None.
        """
        if data is None:
            return None

        if self.source_type is SourceType.GOLD:
            return pd.DataFrame(data)
        if self.source_type is SourceType.EXCHANGE_RATES:
            rates = data[0]["rates"]
            return pd.DataFrame(rates)
        raise ValueError(f"Unsupported source type: {self.source_type}")
    def save_data_to_databricks(
            self,
            df: pd.DataFrame,
            catalog: str,
            schema: str,
            table_name: str,
            mode: Literal["overwrite", "append", "ignore", "error"] = "overwrite"
            ) -> None:
        """Save DataFrame to Databricks Delta table.

        Args:
            df: DataFrame to be saved.
            catalog: Databricks catalog name.
            schema: Target schema name.
            table_name: Target table name.
            mode: Write mode (e.g., "overwrite", "append").

        Returns:
            None
        """
        if df is None:
            print("No data to save")
            return

        full_table_name = f"{catalog}.{schema}.{table_name}"

        df.write.format("delta").mode(mode).saveAsTable(full_table_name)

source = NBPSource(table="A", source_type="EXCHANGE_RATES")

source.get_data()
