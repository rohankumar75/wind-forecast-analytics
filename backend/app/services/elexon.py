import os
from datetime import date, timedelta
import httpx

BASE_URL = os.getenv("ELEXON_BASE_URL", "https://data.elexon.co.uk/bmrs/api/v1").rstrip("/")
TIMEOUT = float(os.getenv("ELEXON_TIMEOUT_SECONDS", "20"))

class ElexonError(RuntimeError):
    pass

def _records(payload):
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict):
        for key in ("data", "results", "items"):
            if isinstance(payload.get(key), list):
                return payload[key]
    return []

def fetch_dataset(dataset: str, start: date, end: date):
    """Fetch dataset stream records. Verify query parameters against current Elexon docs.

    January delivery dates need forecast publications from late December as well.
    This client uses the documented dataset stream path and common from/to parameters.
    If the live API expects different parameter names or paging, update this adapter.
    """
    url = f"{BASE_URL}/datasets/{dataset}/stream"
    params = {"from": start.isoformat(), "to": (end + timedelta(days=1)).isoformat()}
    try:
        with httpx.Client(timeout=TIMEOUT, follow_redirects=True) as client:
            response = client.get(url, params=params)
            response.raise_for_status()
            records = _records(response.json())
    except (httpx.HTTPError, ValueError) as exc:
        raise ElexonError(f"{dataset} request failed: {exc}") from exc
    return records

def fetch_actuals(start: date, end: date):
    rows = fetch_dataset("FUELHH", start, end)
    return [
        row for row in rows
        if str(row.get("fuelType", "")).upper() == "WIND"
        and row.get("startTime") is not None
        and row.get("generation") is not None
    ]

def fetch_forecasts(start: date, end: date):
    rows = fetch_dataset("WINDFOR", start, end)
    return [
        row for row in rows
        if row.get("startTime") is not None
        and row.get("publishTime") is not None
        and row.get("generation") is not None
    ]
