import { useEffect, useMemo, useState } from 'react'
import { CartesianGrid, Legend, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis, Area, AreaChart } from 'recharts'
import { getAnalysis } from './api/client'
import type { Analysis } from './types'

const fmt = (v: number | null | undefined) => v == null ? '—' : new Intl.NumberFormat('en-GB', { maximumFractionDigits: 1 }).format(v)
const shortTime = (s: string) => new Date(s).toLocaleString('en-GB', { day: '2-digit', month: 'short', hour: '2-digit', minute: '2-digit', timeZone: 'UTC' }) + ' UTC'

export default function App() {
  const [start, setStart] = useState('2026-01-01')
  const [end, setEnd] = useState('2026-01-31')
  const [data, setData] = useState<Analysis | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [refresh, setRefresh] = useState(0)

  useEffect(() => {
    let alive = true
    setLoading(true); setError('')
    getAnalysis(start, end)
      .then(result => { if (alive) setData(result) })
      .catch(e => { if (alive) setError(e instanceof Error ? e.message : 'Unable to load analytics') })
      .finally(() => { if (alive) setLoading(false) })
    return () => { alive = false }
  }, [start, end, refresh])

  const chartData = useMemo(() => (data?.data || []).map(p => ({
    ...p, time: new Date(p.startTime).toLocaleString('en-GB', { day: '2-digit', month: 'short', hour: '2-digit', minute: '2-digit', timeZone: 'UTC' })
  })), [data])

  const downloadCsv = () => {
    if (!data) return
    const header = ['startTime','publishTime','forecast_mw','actual_mw','error_mw']
    const rows = data.data.map(p => header.map(k => JSON.stringify((p as any)[k] ?? '')).join(','))
    const blob = new Blob([[header.join(','), ...rows].join('\n')], { type: 'text/csv;charset=utf-8;' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a'); a.href = url; a.download = `wind-forecast-${start}-to-${end}.csv`; a.click()
    URL.revokeObjectURL(url)
  }

  const m = data?.metrics
  return <div className="app-shell">
    <aside className="sidebar">
      <div className="brand"><div className="brand-mark">W</div><div><strong>WindScope</strong><span>ENERGY ANALYTICS</span></div></div>
      <div className="nav-label">WORKSPACE</div>
      <div className="nav-item active"><span>◫</span> Forecast overview</div>
      <div className="side-bottom"><div className="live-dot"></div><span>UK national wind</span><small>30 min intervals</small></div>
    </aside>
    <main className="main">
      <header className="topbar"><div><div className="eyebrow">ENERGY TRADING / ANALYTICS</div><h1>Wind forecast overview</h1><p>Understand forecast performance before day-ahead procurement decisions.</p></div><div className="header-right"><span className="status-pill"><i></i>{data?.source_mode === 'elexon_live' ? 'LIVE SOURCE' : 'DEMO MODE'}</span><button className="secondary-btn" onClick={() => setRefresh(x => x + 1)}>↻ Refresh</button></div></header>
      <section className="filters panel">
        <div className="filter-title"><span className="filter-icon">⌁</span><div><strong>Analysis period</strong><small>Delivery date range · UTC</small></div></div>
        <label>FROM<input type="date" value={start} onChange={e => setStart(e.target.value)} /></label>
        <label>TO<input type="date" value={end} onChange={e => setEnd(e.target.value)} /></label>
        <button className="primary-btn" onClick={() => setRefresh(x => x + 1)}>Apply filters <span>→</span></button>
        <button className="secondary-btn" onClick={downloadCsv} disabled={!data?.data.length}>Export CSV ↓</button>
      </section>
      {error && <div className="error-banner"><strong>Could not load analysis.</strong> {error}</div>}
      {data?.warnings.map((w, i) => <div className="warning-banner" key={i}>ⓘ {w}</div>)}
      {loading && <div className="loading-bar">Loading generation data…</div>}
      <section className="kpi-grid">
        <Kpi title="Mean absolute error" value={fmt(m?.mae_mw)} unit="MW" note="Average absolute forecast error" icon="↕" />
        <Kpi title="Root mean square error" value={fmt(m?.rmse_mw)} unit="MW" note="Penalizes larger misses" icon="⌁" />
        <Kpi title="Forecast bias" value={fmt(m?.bias_mw)} unit="MW" note="Forecast minus actual" icon="±" />
        <Kpi title="Matched intervals" value={fmt(m?.sample_count)} unit="records" note="30-minute matched pairs" icon="▦" />
      </section>
      <section className="content-grid">
        <div className="panel chart-panel">
          <div className="panel-head"><div><h2>Forecast vs actual generation</h2><p>National wind generation · MW</p></div><span className="legend-tag"><i className="blue-dot"></i>Forecast <i className="green-dot"></i>Actual</span></div>
          <div className="chart-wrap">{chartData.length ? <ResponsiveContainer width="100%" height="100%"><LineChart data={chartData} margin={{ top: 12, right: 16, left: 0, bottom: 8 }}><CartesianGrid strokeDasharray="3 3" stroke="#243044" vertical={false}/><XAxis dataKey="time" tick={{ fill: '#8290a6', fontSize: 11 }} tickLine={false} axisLine={false} minTickGap={50}/><YAxis tick={{ fill: '#8290a6', fontSize: 11 }} tickLine={false} axisLine={false} width={52}/><Tooltip contentStyle={{ background: '#111c2e', border: '1px solid #29364b', borderRadius: 10, color: '#f1f5f9' }} labelStyle={{ color: '#a8b5c9' }}/><Legend/><Line type="monotone" dataKey="forecast_mw" name="Forecast" stroke="#6b8cff" strokeWidth={2} dot={false} connectNulls={false}/><Line type="monotone" dataKey="actual_mw" name="Actual" stroke="#35c99a" strokeWidth={2} dot={false} connectNulls={false}/></LineChart></ResponsiveContainer> : <Empty loading={loading} />}</div>
          <div className="chart-foot"><span><i className="blue-dot"></i>Forecast selected at cutoff</span><span><i className="green-dot"></i>Measured actual generation</span></div>
        </div>
        <div className="panel insight-panel">
          <div className="panel-head"><div><h2>Forecast error</h2><p>Forecast − actual · MW</p></div><span className="mini-icon">↗</span></div>
          <div className="error-chart">{chartData.length ? <ResponsiveContainer width="100%" height="100%"><AreaChart data={chartData}><CartesianGrid strokeDasharray="3 3" stroke="#243044" vertical={false}/><XAxis dataKey="time" hide/><YAxis tick={{ fill: '#8290a6', fontSize: 10 }} tickLine={false} axisLine={false} width={48}/><Tooltip contentStyle={{ background: '#111c2e', border: '1px solid #29364b', borderRadius: 10, color: '#f1f5f9' }}/><Area type="monotone" dataKey="error_mw" name="Error (MW)" stroke="#f4b860" fill="#f4b860" fillOpacity={0.12} connectNulls={false}/></AreaChart></ResponsiveContainer> : <Empty loading={loading}/>}</div>
          <div className="insight-copy"><span className="insight-label">HOW TO READ THIS</span><p>Positive error means wind generation was over-forecast. Negative error means it was under-forecast. Procurement impact also depends on demand and other generation.</p></div>
        </div>
      </section>
      <section className="panel table-panel">
        <div className="panel-head table-heading"><div><h2>Forecast audit trail</h2><p>Publication timestamp is shown separately from delivery timestamp.</p></div><span className="count-pill">{data?.data.length ?? 0} intervals</span></div>
        <div className="table-scroll"><table><thead><tr><th>DELIVERY TIME (UTC)</th><th>FORECAST PUBLISHED (UTC)</th><th>FORECAST (MW)</th><th>ACTUAL (MW)</th><th>ERROR (MW)</th></tr></thead><tbody>
          {(data?.data || []).slice(0, 100).map((p, i) => <tr key={`${p.startTime}-${i}`}><td>{shortTime(p.startTime)}</td><td>{p.publishTime ? shortTime(p.publishTime) : '—'}</td><td>{fmt(p.forecast_mw)}</td><td>{fmt(p.actual_mw)}</td><td><span className={`error-value ${(p.error_mw || 0) > 0 ? 'positive' : (p.error_mw || 0) < 0 ? 'negative' : ''}`}>{fmt(p.error_mw)}</span></td></tr>)}
          {!data?.data.length && <tr><td colSpan={5} className="empty-cell">{loading ? 'Loading…' : 'No matched records for this period.'}</td></tr>}
        </tbody></table></div>
        <div className="table-footer">Showing up to 100 rows. Use Export CSV for the full matched series.</div>
      </section>
      <footer>WIND SCOPE <span>•</span> Built for day-ahead renewable generation analysis <span className="footer-right">Data quality matters · Verify source mode before decisions</span></footer>
    </main>
  </div>
}

function Kpi({ title, value, unit, note, icon }: {title: string; value: string; unit: string; note: string; icon: string}) {
  return <div className="panel kpi-card"><div className="kpi-top"><span>{title}</span><b>{icon}</b></div><div className="kpi-value">{value}<small>{unit}</small></div><div className="kpi-note"><span className="note-dot"></span>{note}</div></div>
}
function Empty({ loading }: { loading: boolean }) { return <div className="empty-state">{loading ? 'Loading chart…' : 'No matched data to display'}</div> }
