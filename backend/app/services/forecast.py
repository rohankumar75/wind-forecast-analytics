import os
from datetime import date, datetime, timedelta, timezone
import math
import pandas as pd
from app.services.elexon import fetch_actuals, fetch_forecasts
from app.services.sample_data import sample_records

def _to_frame(rows, time_col, value_col):
    df = pd.DataFrame(rows)
    if df.empty or time_col not in df or value_col not in df:
        return pd.DataFrame(columns=[time_col, value_col])
    df[time_col] = pd.to_datetime(df[time_col], utc=True, errors="coerce")
    df[value_col] = pd.to_numeric(df[value_col], errors="coerce")
    return df.dropna(subset=[time_col, value_col])

def _select_forecasts(forecasts, start, end, cutoff_hour):
    f = _to_frame(forecasts, "startTime", "generation")
    if f.empty or "publishTime" not in f:
        return pd.DataFrame(columns=["startTime", "publishTime", "forecast_mw"])
    f["publishTime"] = pd.to_datetime(f["publishTime"], utc=True, errors="coerce")
    f = f.dropna(subset=["publishTime"])
    start_dt = pd.Timestamp(datetime.combine(start, datetime.min.time()), tz="UTC")
    end_dt = pd.Timestamp(datetime.combine(end + timedelta(days=1), datetime.min.time()), tz="UTC")
    f = f[(f["startTime"] >= start_dt) & (f["startTime"] < end_dt)]
    # For each delivery date, only publications available at the configurable cutoff are eligible.
    f["delivery_date"] = f["startTime"].dt.date
    f["cutoff"] = pd.to_datetime(f["delivery_date"].astype(str), utc=True) + pd.to_timedelta(cutoff_hour, unit="h")
    f = f[f["publishTime"] <= f["cutoff"]]
    f = f.sort_values("publishTime").drop_duplicates("startTime", keep="last")
    return f.rename(columns={"generation": "forecast_mw"})[["startTime", "publishTime", "forecast_mw"]]

def build_analysis(start: date, end: date, cutoff_hour_utc: int = 10, live: bool = False):
    warnings = []
    use_sample = os.getenv("USE_SAMPLE_DATA", "true").lower() == "true" and not live
    mode = "synthetic_demo"
    if use_sample:
        actual_rows, forecast_rows = sample_records(start, end)
        warnings.append("Synthetic demo data is being shown; it is not live Elexon data.")
    else:
        # Forecast publication history can begin before the delivery window.
        try:
            actual_rows = fetch_actuals(start, end)
            forecast_rows = fetch_forecasts(start - timedelta(days=2), end)
            mode = "elexon_live"
        except Exception as exc:
            if live:
                raise
            warnings.append(f"Live Elexon retrieval failed: {exc}")
            actual_rows, forecast_rows = sample_records(start, end)
            mode = "synthetic_fallback"
            warnings.append("Synthetic fallback data is being shown; it is not live Elexon data.")

    a = _to_frame(actual_rows, "startTime", "generation")
    if not a.empty:
        a = a.rename(columns={"generation": "actual_mw"})
        a = a.drop_duplicates("startTime", keep="last")
    f = _select_forecasts(forecast_rows, start, end, cutoff_hour_utc)
    if not a.empty:
        a = a[(a["startTime"] >= pd.Timestamp(start, tz="UTC")) &
              (a["startTime"] < pd.Timestamp(end + timedelta(days=1), tz="UTC"))]
    merged = pd.merge(f, a[["startTime", "actual_mw"]] if not a.empty else
                      pd.DataFrame(columns=["startTime", "actual_mw"]), on="startTime", how="inner")
    merged["error_mw"] = merged["forecast_mw"] - merged["actual_mw"]
    n = len(merged)
    metrics = {
        "mae_mw": round(float(merged["error_mw"].abs().mean()), 3) if n else None,
        "rmse_mw": round(float(math.sqrt((merged["error_mw"] ** 2).mean())), 3) if n else None,
        "bias_mw": round(float(merged["error_mw"].mean()), 3) if n else None,
        "sample_count": n,
    }
    merged = merged.sort_values("startTime")
    points = []
    for _, row in merged.iterrows():
        points.append({
            "startTime": row["startTime"].isoformat().replace("+00:00", "Z"),
            "publishTime": row["publishTime"].isoformat().replace("+00:00", "Z"),
            "forecast_mw": round(float(row["forecast_mw"]), 3),
            "actual_mw": round(float(row["actual_mw"]), 3),
            "error_mw": round(float(row["error_mw"]), 3),
        })
    daily = []
    if n:
        merged["day"] = merged["startTime"].dt.strftime("%Y-%m-%d")
        for day, group in merged.groupby("day"):
            daily.append({
                "date": day,
                "mae_mw": round(float(group["error_mw"].abs().mean()), 3),
                "rmse_mw": round(float(math.sqrt((group["error_mw"] ** 2).mean())), 3),
                "bias_mw": round(float(group["error_mw"].mean()), 3),
                "sample_count": int(len(group)),
            })
    return {
        "period": {"start": start.isoformat(), "end": end.isoformat(),
                   "cutoff_hour_utc": cutoff_hour_utc},
        "metrics": metrics, "data": points, "daily_accuracy": daily,
        "source_mode": mode, "warnings": warnings,
    }
