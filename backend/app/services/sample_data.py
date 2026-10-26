from datetime import datetime, timedelta, timezone

def sample_records(start, end):
    """Deterministic synthetic demo data. Never presented as live Elexon data."""
    actuals, forecasts = [], []
    current = datetime.combine(start, datetime.min.time(), tzinfo=timezone.utc)
    finish = datetime.combine(end + timedelta(days=1), datetime.min.time(), tzinfo=timezone.utc)
    i = 0
    while current < finish:
        # A smooth synthetic curve solely to make the UI usable without network access.
        actual = 6500 + 1800 * __import__("math").sin(i / 23) + 650 * __import__("math").sin(i / 7)
        actuals.append({"startTime": current.isoformat().replace("+00:00", "Z"),
                        "generation": round(actual, 2), "fuelType": "WIND"})
        pub = current - timedelta(days=1, hours=1)
        forecasts.append({"startTime": current.isoformat().replace("+00:00", "Z"),
                          "publishTime": pub.isoformat().replace("+00:00", "Z"),
                          "generation": round(actual + 300 * __import__("math").sin(i / 5) + 120, 2)})
        current += timedelta(minutes=30)
        i += 1
    return actuals, forecasts
