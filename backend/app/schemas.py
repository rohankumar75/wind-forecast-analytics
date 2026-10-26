from pydantic import BaseModel
from typing import Optional

class DataPoint(BaseModel):
    startTime: str
    publishTime: Optional[str] = None
    forecast_mw: Optional[float] = None
    actual_mw: Optional[float] = None
    error_mw: Optional[float] = None

class Metrics(BaseModel):
    mae_mw: Optional[float] = None
    rmse_mw: Optional[float] = None
    bias_mw: Optional[float] = None
    sample_count: int = 0

class ForecastResponse(BaseModel):
    period: dict
    metrics: Metrics
    data: list[DataPoint]
    source_mode: str
    warnings: list[str] = []
