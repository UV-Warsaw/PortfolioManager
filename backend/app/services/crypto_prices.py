"""Fetch live BTC/ETH prices from the CoinGecko free public API."""

import httpx

from app.schemas.portfolio import CryptoPricesResponse

_COINGECKO_URL = (
    "https://api.coingecko.com/api/v3/simple/price"
    "?ids=bitcoin,ethereum&vs_currencies={currency}"
)
_TIMEOUT = 10.0  # seconds


def fetch_crypto_prices(currency: str = "PLN") -> CryptoPricesResponse:
    """Fetch current BTC and ETH prices from CoinGecko.

    Uses the free CoinGecko public API (no API key required).

    Args:
        currency: Target currency code, e.g. 'PLN', 'USD', 'EUR'.

    Returns:
        CryptoPricesResponse with BTC and ETH prices.

    Raises:
        RuntimeError: If the upstream request fails or returns unexpected data.
    """
    url = _COINGECKO_URL.format(currency=currency.lower())
    try:
        with httpx.Client(timeout=_TIMEOUT) as client:
            resp = client.get(url)
            resp.raise_for_status()
            data = resp.json()
    except httpx.HTTPError as exc:
        raise RuntimeError(f"CoinGecko request failed: {exc}") from exc

    key = currency.lower()
    try:
        btc = float(data["bitcoin"][key])
        eth = float(data["ethereum"][key])
    except (KeyError, TypeError, ValueError) as exc:
        raise RuntimeError(f"Unexpected CoinGecko response format: {data}") from exc

    return CryptoPricesResponse(BTC=btc, ETH=eth, currency=currency.upper())
