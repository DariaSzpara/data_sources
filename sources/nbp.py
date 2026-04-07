import requests
from typing import Literal
from enum import Enum
import pandas as pd

class SourceType(Enum):
    GOLD = "GOLD"
    EXCHANGE_RATES = "EXCHANGE_RATES"

class NBPSource:
    def __init__(self, table:Literal["A","B","C"], source_type:SourceType):
        self.table = table
        self.source_type = source_type
        if self.source_type is SourceType.GOLD:
            self.url = "https://api.nbp.pl/api/cenyzlota"
        elif self.source_type is SourceType.EXCHANGE_RATES:
            self.url = f"http://api.nbp.pl/api/exchangerates/tables/{self.table}/"
    def get_data(self):
        headers = {
            "Accept": "application/json"
            }
        response = requests.get(self.url,headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error: {response.status_code}")
            return None

    def transform_data_to_df(self,data):
        if data is None:
            return None
        
        if self.source_type is SourceType.GOLD:
            return pd.DataFrame(data)
        elif self.source_type is SourceType.EXCHANGE_RATES:
            rates = data[0]["rates"]
            return pd.DataFrame(rates)

    def save_data_to_databricks(self, df, catalog, schema, table_name, mode="overwrite"):
        if df is None:
            print("No data to save")
            return

        full_table_name = f"{catalog}.{schema}.{table_name}"

        df.write.format("delta").mode(mode).saveAsTable(full_table_name)
