from datetime import date
from app.services.forecast import build_analysis

def test_sample_analysis_has_expected_shape(monkeypatch):
    monkeypatch.setenv("USE_SAMPLE_DATA", "true")
    result = build_analysis(date(2026, 1, 1), date(2026, 1, 1), 10, False)
    assert result["source_mode"] == "synthetic_demo"
    assert result["metrics"]["sample_count"] > 0
    assert result["metrics"]["mae_mw"] is not None
    assert result["data"][0]["forecast_mw"] is not None
    assert result["data"][0]["actual_mw"] is not None

def test_error_formula():
    forecast = [100, 200]
    actual = [90, 220]
    errors = [f-a for f, a in zip(forecast, actual)]
    assert sum(abs(x) for x in errors) / len(errors) == 15
    assert round((sum(x*x for x in errors) / len(errors)) ** 0.5, 2) == 15.81
    assert sum(errors) / len(errors) == -5
