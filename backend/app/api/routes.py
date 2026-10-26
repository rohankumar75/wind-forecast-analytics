from datetime import date
from fastapi import APIRouter, HTTPException, Query
from app.services.forecast import build_analysis

router = APIRouter()

@router.get("/health")
def health():
    return {"status": "ok"}

def _analysis(start: date, end: date, cutoff_hour_utc: int, live: bool):
    if end < start:
        raise HTTPException(status_code=400, detail="'end' must be on or after 'start'")
    if (end - start).days > 90:
        raise HTTPException(status_code=400, detail="Date range limited to 90 days per request")
    try:
        return build_analysis(start, end, cutoff_hour_utc, live)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Could not build analysis: {exc}") from exc

@router.get("/forecast/summary")
def summary(
    start: date = Query(date(2026, 1, 1)),
    end: date = Query(date(2026, 1, 31)),
    cutoff_hour_utc: int = Query(10, ge=0, le=23),
    live: bool = False,
):
    result = _analysis(start, end, cutoff_hour_utc, live)
    return {"period": result["period"], "metrics": result["metrics"],
            "source_mode": result["source_mode"], "warnings": result["warnings"]}

@router.get("/forecast/series")
def series(
    start: date = Query(date(2026, 1, 1)),
    end: date = Query(date(2026, 1, 31)),
    cutoff_hour_utc: int = Query(10, ge=0, le=23),
    live: bool = False,
):
    return _analysis(start, end, cutoff_hour_utc, live)

@router.get("/forecast/history")
def history(
    start: date = Query(date(2026, 1, 1)),
    end: date = Query(date(2026, 1, 31)),
    cutoff_hour_utc: int = Query(10, ge=0, le=23),
    live: bool = False,
):
    result = _analysis(start, end, cutoff_hour_utc, live)
    return {"period": result["period"], "data": result["data"],
            "source_mode": result["source_mode"], "warnings": result["warnings"]}

@router.get("/forecast/accuracy")
def accuracy(
    start: date = Query(date(2026, 1, 1)),
    end: date = Query(date(2026, 1, 31)),
    cutoff_hour_utc: int = Query(10, ge=0, le=23),
    live: bool = False,
):
    result = _analysis(start, end, cutoff_hour_utc, live)
    return {"period": result["period"], "daily_accuracy": result["daily_accuracy"],
            "source_mode": result["source_mode"], "warnings": result["warnings"]}
