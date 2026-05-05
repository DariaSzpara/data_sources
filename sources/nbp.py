"""NBP data ingestion module.

This module provides functionality to:
- fetch data from the NBP API,
- transform it into pandas DataFrames,
- save results to Databricks Delta tables.

Supported data sources:
- gold prices,
- exchange rates (tables A, B, C).
"""
import requests
from typing import Literal
import pandas as pd


class NBPSource:
    def __init__(self, table:Literal["A","B","C"]):
        self.table = table
    
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
        response.raise_for_status()
        return response.json()
    
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


class NBPHistorySource(NBPSource):
    BASE_URL = "https://api.nbp.pl/api/exchangerates/tables"

    def __init__(self, table: Literal['A', 'B', 'C'],start_date=None, end_date=None):
        self.table = table
        if start_date and end_date:
            self.url =  f"{self.BASE_URL}/{self.table}/{start_date}/{end_date}/"
        elif start_date:
            self.url = f"{self.BASE_URL}/{self.table}/{start_date}/"
        else:
            self.url = f"{self.BASE_URL}/{self.table}/today/"
        
    def transform_data_to_df(self, data):

        if data is None:
            raise ValueError('No data to transform')
        rows = []

        for table in data:
            date = table["effectiveDate"]

            for rate in table["rates"]:
                rows.append({
                    "date": date,
                    "currency": rate["currency"],
                    "code": rate["code"],
                    "mid": rate["mid"]
                })

        return pd.DataFrame(rows)
    
class NBPGold(NBPSource):
    BASE_URL = "https://api.nbp.pl/api/cenyzlota"

    def __init__(self, start_date=None, end_date=None):
        self.table = None
        if start_date is None and end_date is None:
            self.url = f"{self.BASE_URL}/"
        elif start_date and end_date is None:
            self.url = f"{self.BASE_URL}/{start_date}/"
        else:
            self.url = f"{self.BASE_URL}/{start_date}/{end_date}/"

    def transform_data_to_df(self, data: list[dict]) -> pd.DataFrame:
        if data is None:
            raise ValueError("No data to transform")

        return pd.DataFrame([
            {
                "date": item["data"],
                "price": item["cena"]
            }
            for item in data
        ])

class NBPCurrent(NBPSource):
    def __init__(self, table):
        self.table = table
        self.url = f"http://api.nbp.pl/api/exchangerates/tables/{self.table}/"
    def transform_data_to_df(self,data: list[dict]) -> pd.DataFrame:
        if data is None:
            raise ValueError("transform_data_to_df() requires non-None data")
        rates = data[0]["rates"]
        return pd.DataFrame(rates)
