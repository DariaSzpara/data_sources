"""Cryptocurrency data source module."""

import requests


class CryptoCurrency:
    """Class for fetching cryptocurrency market data."""

    def get_data(self) -> dict:
        """Fetch cryptocurrency data from Alpha Vantage API.

        Returns:
            API response parsed as JSON.
        """
        headers = {
            "Accept": "application/json",
            "Authorization": "Bearer BAUP2ZFEK2L46MXK",
        }

        response = requests.get(
            (
                "https://www.alphavantage.co/query"
                "?function=DIGITAL_CURRENCY_DAILY"
                "&symbol=BTC"
                "&market=EUR"
                "&apikey=BAUP2ZFEK2L46MXK"
            ),
            headers=headers,
            timeout=30,
        )

        response.raise_for_status()

        return response.json()
