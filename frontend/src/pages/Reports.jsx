import React, { useState, useEffect } from 'react'
import { reportsApi, aiApi } from '../services/api'
import { formatCurrency, formatNumber } from '../utils/formatters'
import { ReportBuilderPanel } from '../components/reports/ReportBuilderPanel'
import {
  FileDown,
  FileSpreadsheet,
  TrendingUp,
  Sparkles,
  Calendar,
  Download,
  CheckCircle,
} from 'lucide-react'

export const Reports = () => {
  const [reportData, setReportData] = useState(null)
  const [forecast, setForecast] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [downloadingPdf, setDownloadingPdf] = useState(false)

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true)
        const [repRes, foreRes] = await Promise.all([
          reportsApi.getMonthlyData(),
          aiApi.getForecast(),
        ])
        setReportData(repRes.data)
        setForecast(foreRes.data)
      } catch (err) {
        setError(err.message || 'Failed to load report data.')
      } finally {
        setLoading(false)
      }
    }
    fetchData()
  }, [])

  const handleDownloadPdf = async () => {
    try {
      setDownloadingPdf(true)
      await reportsApi.downloadPdf({ period_title: 'Executive Sales Report 2026' })
    } catch (e) {
      alert(e.message || 'Error generating PDF download')
    } finally {
      setDownloadingPdf(false)
    }
  }

  const handleDownloadCsv = async () => {
    try {
      await reportsApi.downloadCsv({})
    } catch (e) {
      alert(e.message || 'Error generating CSV download')
    }
  }

  return (
    <div className="space-y-5 max-w-4xl">
      {/* Header */}
      <div>
        <h1 className="text-xl font-bold text-text tracking-tight">
          Intelligence Reports & Export
        </h1>
        <p className="text-xs text-text-muted mt-0.5">
          Build custom reports with flexible filters, plus AI-generated executive summaries and ML forecasts
        </p>
      </div>

      <ReportBuilderPanel />

      {error && (
        <div className="p-4 bg-danger-bg border border-[#F3C7BD] text-danger rounded-xl text-xs font-semibold">
          {error}
        </div>
      )}

      {loading ? (
        <div className="space-y-4 animate-pulse">
          <div className="h-44 bg-slate-200 rounded-xl"></div>
          <div className="h-44 bg-slate-200 rounded-xl"></div>
        </div>
      ) : (
        <div className="space-y-5">
          <div className="flex items-center justify-between gap-3 pt-2 border-t border-border">
            <h4 className="font-bold text-sm text-text pt-3">Monthly Executive Report</h4>
            <div className="flex items-center gap-2 pt-3">
              <button
                onClick={handleDownloadCsv}
                className="flex items-center gap-1.5 px-3.5 py-2 bg-surface border border-border hover:bg-slate-50 text-text font-bold text-xs rounded-lg shadow-xs transition-colors"
              >
                <FileSpreadsheet className="w-3.5 h-3.5 text-success" />
                <span>Export CSV</span>
              </button>
              <button
                onClick={handleDownloadPdf}
                disabled={downloadingPdf}
                className="flex items-center gap-1.5 px-4 py-2 bg-primary hover:bg-primary-light disabled:opacity-50 text-white font-bold text-xs rounded-lg shadow-xs transition-colors"
              >
                <FileDown className="w-4 h-4 text-[#7FB6FF]" />
                <span>{downloadingPdf ? 'Generating…' : 'Export PDF'}</span>
              </button>
            </div>
          </div>
          {/* ML Revenue Forecaster Card */}
          {forecast && (
            <div className="bg-surface border border-border rounded-xl p-5 shadow-sm">
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-2">
                  <TrendingUp className="w-4 h-4 text-secondary" />
                  <h4 className="font-bold text-xs sm:text-[13px] text-text">
                    AI Revenue Forecaster (Scikit-Learn)
                  </h4>
                </div>
                <span className="text-[10.5px] font-bold bg-secondary/15 text-secondary px-2.5 py-0.5 rounded-full uppercase">
                  {forecast.status}
                </span>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 p-4 bg-slate-50 border border-border rounded-xl mb-3">
                <div>
                  <span className="text-[11px] font-bold text-text-muted uppercase tracking-wider block">
                    Target Period
                  </span>
                  <span className="font-mono text-base font-bold text-primary">
                    {forecast.next_month}
                  </span>
                </div>
                <div>
                  <span className="text-[11px] font-bold text-text-muted uppercase tracking-wider block">
                    Projected Revenue
                  </span>
                  <span className="font-mono text-xl font-bold text-secondary">
                    {formatCurrency(forecast.predicted_revenue)}
                  </span>
                </div>
                <div>
                  <span className="text-[11px] font-bold text-text-muted uppercase tracking-wider block">
                    Expected Growth
                  </span>
                  <span
                    className={`font-mono text-base font-bold ${
                      forecast.growth_estimate_pct >= 0 ? 'text-success' : 'text-danger'
                    }`}
                  >
                    {forecast.growth_estimate_pct >= 0 ? '+' : ''}
                    {forecast.growth_estimate_pct}%
                  </span>
                </div>
              </div>

              <p className="text-xs text-text-muted">
                Model: <span className="font-semibold text-text">{forecast.model_name}</span>
                {forecast.r2_score !== null && (
                  <span> (R² Score: {forecast.r2_score})</span>
                )}
                {' — '}{forecast.message}
              </p>
            </div>
          )}

          {/* AI Executive Summary Card */}
          {reportData && (
            <div className="bg-surface border border-border rounded-xl p-5 shadow-sm">
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-2">
                  <Sparkles className="w-4 h-4 text-secondary" />
                  <h4 className="font-bold text-xs sm:text-[13px] text-text">
                    Executive Intelligence Summary
                  </h4>
                </div>
                <span className="text-[10px] font-bold bg-secondary text-white px-2 py-0.5 rounded-full uppercase">
                  Verified Analysis
                </span>
              </div>
              <p className="text-xs sm:text-[13px] text-[#23344f] leading-relaxed bg-[#F4F8FD] border border-[#D6E4F5] p-4 rounded-xl">
                {reportData.ai_executive_summary}
              </p>
            </div>
          )}

          {/* KPI Snapshot Table */}
          {reportData?.summary_kpis && (
            <div className="bg-surface border border-border rounded-xl p-5 shadow-sm">
              <h4 className="font-bold text-xs sm:text-[13px] text-text mb-3">
                Monthly Performance Snapshot
              </h4>
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                <div className="p-3.5 bg-slate-50 border border-border rounded-lg">
                  <div className="text-[11px] font-bold text-text-muted uppercase">
                    Total Revenue
                  </div>
                  <div className="font-mono text-xl font-bold text-primary mt-1">
                    {formatCurrency(reportData.summary_kpis.total_revenue)}
                  </div>
                </div>
                <div className="p-3.5 bg-slate-50 border border-border rounded-lg">
                  <div className="text-[11px] font-bold text-text-muted uppercase">
                    Total Completed Orders
                  </div>
                  <div className="font-mono text-xl font-bold text-text mt-1">
                    {formatNumber(reportData.summary_kpis.total_orders)}
                  </div>
                </div>
                <div className="p-3.5 bg-slate-50 border border-border rounded-lg">
                  <div className="text-[11px] font-bold text-text-muted uppercase">
                    Average Order Value (AOV)
                  </div>
                  <div className="font-mono text-xl font-bold text-secondary mt-1">
                    {formatCurrency(reportData.summary_kpis.average_order_value)}
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
