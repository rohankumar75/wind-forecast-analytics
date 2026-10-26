export type Point = {
  startTime: string
  publishTime?: string | null
  forecast_mw: number | null
  actual_mw: number | null
  error_mw: number | null
}
export type Analysis = {
  period: { start: string; end: string; cutoff_hour_utc: number }
  metrics: { mae_mw: number | null; rmse_mw: number | null; bias_mw: number | null; sample_count: number }
  data: Point[]
  daily_accuracy: Array<{date: string; mae_mw: number; rmse_mw: number; bias_mw: number; sample_count: number}>
  source_mode: string
  warnings: string[]
}
