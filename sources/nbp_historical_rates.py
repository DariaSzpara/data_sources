import requests
from typing import Literal
import pandas as pd

class NBPHistorySource:
    BASE_URL = "https://api.nbp.pl/api/exchangerates/tables"

    def __init__(self, table: Literal['A', 'B', 'C']):
        self.table = table

    def build_url(self, start_date=None, end_date=None):
        if start_date and end_date:
            return f"{self.BASE_URL}/{self.table}/{start_date}/{end_date}/"
        elif start_date:
            return f"{self.BASE_URL}/{self.table}/{start_date}/"
        else:
            return f"{self.BASE_URL}/{self.table}/today/"
        
    def fetch(self, start_date=None, end_date=None):
        url = self.build_url(start_date, end_date)

        response = requests.get(url, headers={"Accept": "application/json"})

        if response.status_code == 404:
            return []

        response.raise_for_status()
        return response.json()
    def transform_to_df(self, data):
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
