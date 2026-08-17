import React, { useState, useEffect, useMemo } from 'react'
import { analyticsApi, regionsApi, productsApi } from '../services/api'
import { formatCurrency } from '../utils/formatters'
import { FlaskConical, RotateCcw, TrendingUp, TrendingDown, Info, Minus, Plus } from 'lucide-react'

const CLAMP = (v, min, max) => Math.min(max, Math.max(min, v))

// Bipolar slider: value range is min..max, center=0 shown as visual midpoint
const BiSlider = ({ label, value, onChange, min, max, step = 1, hint }) => {
  const pct = ((value - min) / (max - min)) * 100
  const zeroPct = ((-min) / (max - min)) * 100
  const positive = value > 0
  const negative = value < 0
  const fillLeft = Math.min(pct, zeroPct)
  const fillWidth = Math.abs(pct - zeroPct)

  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between">
        <span className="text-sm font-semibold text-text">{label}</span>
        <div className="flex items-center gap-1.5">
          <button
            type="button"
            onClick={() => onChange(CLAMP(value - step, min, max))}
            className="w-6 h-6 flex items-center justify-center rounded border border-border text-text-muted hover:border-secondary hover:text-secondary transition-colors"
          >
            <Minus className="w-3 h-3" />
          </button>
          <span className={`w-16 text-center text-sm font-bold tabular-nums ${positive ? 'text-success' : negative ? 'text-danger' : 'text-text-muted'}`}>
            {value > 0 ? '+' : ''}{value}%
          </span>
          <button
            type="button"
            onClick={() => onChange(CLAMP(value + step, min, max))}
            className="w-6 h-6 flex items-center justify-center rounded border border-border text-text-muted hover:border-secondary hover:text-secondary transition-colors"
          >
            <Plus className="w-3 h-3" />
          </button>
        </div>
      </div>

      {/* Custom slider track with zero marker */}
      <div className="relative h-5 flex items-center">
        <div className="w-full h-1.5 bg-border rounded-full relative overflow-hidden">
          <div
            className={`absolute h-full rounded-full transition-all ${positive ? 'bg-success' : negative ? 'bg-danger' : 'bg-border'}`}
            style={{ left: `${fillLeft}%`, width: `${fillWidth}%` }}
          />
        </div>
        {/* Zero tick */}
        <div
          className="absolute w-px h-3 bg-text-dim"
          style={{ left: `${zeroPct}%` }}
        />
        <input
          type="range" min={min} max={max} step={step} value={value}
          onChange={e => onChange(Number(e.target.value))}
          className="absolute w-full h-5 opacity-0 cursor-pointer"
        />
      </div>

      <div className="flex justify-between text-[10px] text-text-dim">
        <span>{min}%</span>
        <span className="text-text-dim/60">0</span>
        <span>+{max}%</span>
      </div>

      {hint && <p className="text-[11px] text-text-dim leading-relaxed">{hint}</p>}
    </div>
  )
}

// Unipolar slider: 0..max only (for things that can't be negative)
const UniSlider = ({ label, value, onChange, min = 0, max, step = 1, hint }) => (
  <div className="space-y-2">
    <div className="flex items-center justify-between">
      <span className="text-sm font-semibold text-text">{label}</span>
      <div className="flex items-center gap-1.5">
        <button
          type="button"
          onClick={() => onChange(CLAMP(value - step, min, max))}
          className="w-6 h-6 flex items-center justify-center rounded border border-border text-text-muted hover:border-secondary hover:text-secondary transition-colors"
        >
          <Minus className="w-3 h-3" />
        </button>
        <span className="w-16 text-center text-sm font-bold tabular-nums text-secondary">
          +{value}%
        </span>
        <button
          type="button"
          onClick={() => onChange(CLAMP(value + step, min, max))}
          className="w-6 h-6 flex items-center justify-center rounded border border-border text-text-muted hover:border-secondary hover:text-secondary transition-colors"
        >
          <Plus className="w-3 h-3" />
        </button>
      </div>
    </div>
    <div className="relative h-5 flex items-center">
      <div className="w-full h-1.5 bg-border rounded-full relative overflow-hidden">
        <div
          className="absolute h-full rounded-full bg-secondary transition-all"
          style={{ left: 0, width: `${((value - min) / (max - min)) * 100}%` }}
        />
      </div>
      <input
        type="range" min={min} max={max} step={step} value={value}
        onChange={e => onChange(Number(e.target.value))}
        className="absolute w-full h-5 opacity-0 cursor-pointer"
      />
    </div>
    <div className="flex justify-between text-[10px] text-text-dim">
      <span>{min}%</span>
      <span>+{max}%</span>
    </div>
    {hint && <p className="text-[11px] text-text-dim leading-relaxed">{hint}</p>}
  </div>
)

const DeltaBar = ({ label, base, scenario, fmt }) => {
  const maxVal = Math.max(base, scenario, 1)
  const basePct = (base / maxVal) * 100
  const scenarioPct = (scenario / maxVal) * 100
  const up = scenario >= base
  return (
    <div className="space-y-1">
      <div className="flex items-center justify-between text-xs">
        <span className="text-text-muted">{label}</span>
        <span className={`font-bold tabular-nums ${up ? 'text-success' : 'text-danger'}`}>
          {fmt(scenario)}
        </span>
      </div>
      <div className="space-y-1">
        <div className="h-1.5 bg-border rounded-full overflow-hidden">
          <div className="h-full rounded-full bg-text-dim/40 transition-all" style={{ width: `${basePct}%` }} />
        </div>
        <div className="h-1.5 bg-border rounded-full overflow-hidden">
          <div className={`h-full rounded-full transition-all ${up ? 'bg-success' : 'bg-danger'}`} style={{ width: `${scenarioPct}%` }} />
        </div>
      </div>
      <div className="flex justify-between text-[10px] text-text-dim">
        <span>Baseline: {fmt(base)}</span>
        <span className={up ? 'text-success' : 'text-danger'}>
          {up ? '+' : ''}{base ? (((scenario - base) / base) * 100).toFixed(1) : '0'}%
        </span>
      </div>
    </div>
  )
}

export const ScenarioLab = () => {
  const [baseline, setBaseline] = useState(null)
  const [regions, setRegions] = useState([])
  const [products, setProducts] = useState([])
  const [loading, setLoading] = useState(true)

  const [scenarioName, setScenarioName] = useState('My Scenario')
  const [selectedRegion, setSelectedRegion] = useState('')
  const [selectedCategory, setSelectedCategory] = useState('')

  // Parameters — all in %
  const [priceChange, setPriceChange] = useState(0)       // -50..+50
  const [demandChange, setDemandChange] = useState(0)     // -50..+100
  const [marketingLift, setMarketingLift] = useState(0)   // 0..50 (campaign demand boost)
  const [newStreams, setNewStreams] = useState(0)          // 0..50 (additive new revenue %)

  const categories = [...new Set(products.map(p => p.category).filter(Boolean))].sort()
  const hasAnyParam = priceChange !== 0 || demandChange !== 0 || marketingLift !== 0 || newStreams !== 0

  const reset = () => {
    setPriceChange(0)
    setDemandChange(0)
    setMarketingLift(0)
    setNewStreams(0)
    setScenarioName('My Scenario')
  }

  useEffect(() => {
    const load = async () => {
      setLoading(true)
      const [kpiRes, regRes, prodRes] = await Promise.allSettled([
        analyticsApi.getSummary({}),
        regionsApi.list(),
        productsApi.list(),
      ])
      if (kpiRes.status === 'fulfilled') setBaseline(kpiRes.value.data)
      if (regRes.status === 'fulfilled') setRegions(regRes.value.data || [])
      if (prodRes.status === 'fulfilled') setProducts(prodRes.value.data || [])
      setLoading(false)
    }
    load()
  }, [])

  // Live simulation (no Run button needed)
  const sim = useMemo(() => {
    if (!baseline) return null

    const baseRevenue = baseline.total_revenue || 0
    const baseOrders  = baseline.total_orders  || 0
    const baseAov     = baseline.average_order_value || 0

    // 1. Price change → AOV shifts directly
    const newAov = baseAov * (1 + priceChange / 100)

    // 2. Demand drivers:
    //    - Direct demand change (distribution, stock)
    //    - Price elasticity: each 1% price rise → -0.8% demand
    //    - Marketing campaign: each 1% marketing "reach" → +0.4% demand lift (diminishing)
    const elasticity   = 1 - (priceChange * 0.8 / 100)
    const directDemand = 1 + demandChange / 100
    const marketDemand = 1 + (marketingLift * 0.4 / 100)
    const newOrders    = Math.max(0, Math.round(baseOrders * directDemand * elasticity * marketDemand))

    // 3. Core estimated revenue = new orders × new AOV
    const coreRevenue = newOrders * newAov

    // 4. New revenue streams: ADDITIVE % of baseline (not a multiplier on scenario revenue)
    //    e.g. +10% means you're adding 10% of baseline from new sources
    const additionalRevenue = baseRevenue * (newStreams / 100)
    const finalRevenue = coreRevenue + additionalRevenue

    const revDiff    = finalRevenue - baseRevenue
    const revDiffPct = baseRevenue ? (revDiff / baseRevenue * 100) : 0
    const orderDiff  = newOrders - baseOrders
    const aovDiff    = newAov - baseAov

    return {
      base: { revenue: baseRevenue, orders: baseOrders, aov: baseAov },
      scenario: { revenue: finalRevenue, orders: newOrders, aov: newAov },
      delta: { revenue: revDiff, revPct: revDiffPct, orders: orderDiff, aov: aovDiff },
      breakdown: {
        core: coreRevenue,
        addl: additionalRevenue,
      },
    }
  }, [baseline, priceChange, demandChange, marketingLift, newStreams])

  return (
    <div className="space-y-5 max-w-5xl">
      {/* Header */}
      <div className="flex items-start justify-between gap-4">
        <div className="flex items-start gap-3">
          <div className="w-9 h-9 rounded-lg bg-signal-actionBg flex items-center justify-center flex-shrink-0 mt-0.5">
            <FlaskConical className="w-5 h-5 text-signal-action" />
          </div>
          <div>
            <h1 className="text-xl font-bold text-text tracking-tight">Scenario Lab</h1>
            <p className="text-xs text-text-dim mt-0.5">What-if simulations — results update live as you adjust</p>
          </div>
        </div>
        {hasAnyParam && (
          <button
            onClick={reset}
            className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold text-text-muted border border-border rounded hover:border-secondary hover:text-text transition-colors"
          >
            <RotateCcw className="w-3 h-3" />
            Reset
          </button>
        )}
      </div>

      {/* Disclaimer */}
      <div className="flex items-start gap-2.5 px-3.5 py-3 bg-signal-actionBg border border-purple-200 rounded-lg text-[11px] text-text-muted leading-relaxed">
        <Info className="w-3.5 h-3.5 text-signal-action flex-shrink-0 mt-0.5" />
        <span>
          <strong className="text-text">SIMULATION — not an actual forecast.</strong>{' '}
          Results are computed using simplified business relationships (price elasticity ≈ 0.8×, marketing lift ≈ 0.4× per reach %). Real outcomes depend on market dynamics not modelled here.
        </span>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-5 gap-5">
        {/* Left: Controls */}
        <div className="lg:col-span-3 space-y-4">
          {/* Scope */}
          <div className="card p-4 space-y-4">
            <h3 className="text-sm font-bold text-text border-b border-border pb-2">Scenario Configuration</h3>
            <div>
              <label className="section-label block mb-1.5">Scenario Name</label>
              <input
                value={scenarioName}
                onChange={e => setScenarioName(e.target.value)}
                placeholder="My Scenario"
                className="w-full bg-sunken border border-border rounded px-3 py-2 text-sm text-text font-medium focus:outline-none focus:border-secondary"
              />
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="section-label block mb-1.5">Region Scope</label>
                <select value={selectedRegion} onChange={e => setSelectedRegion(e.target.value)}
                  className="w-full bg-sunken border border-border rounded px-2.5 py-1.5 text-sm text-text focus:outline-none focus:border-secondary">
                  <option value="">All Regions</option>
                  {regions.map(r => <option key={r.id} value={r.id}>{r.name}</option>)}
                </select>
              </div>
              <div>
                <label className="section-label block mb-1.5">Category Scope</label>
                <select value={selectedCategory} onChange={e => setSelectedCategory(e.target.value)}
                  className="w-full bg-sunken border border-border rounded px-2.5 py-1.5 text-sm text-text focus:outline-none focus:border-secondary">
                  <option value="">All Categories</option>
                  {categories.map(c => <option key={c} value={c}>{c}</option>)}
                </select>
              </div>
            </div>
          </div>

          {/* Sliders */}
          <div className="card p-4 space-y-6">
            <h3 className="text-sm font-bold text-text border-b border-border pb-2">Parameters</h3>

            <BiSlider
              label="Price Change"
              value={priceChange}
              onChange={setPriceChange}
              min={-50} max={50}
              hint="Shifts average order value up or down. Each +1% price rise reduces demand by ~0.8% (mild elasticity)."
            />

            <BiSlider
              label="Demand / Volume Change"
              value={demandChange}
              onChange={setDemandChange}
              min={-50} max={100}
              hint="Direct order volume change — new distribution channels, inventory restocking, market expansion, or demand contraction."
            />

            <UniSlider
              label="Marketing Campaign Lift"
              value={marketingLift}
              onChange={setMarketingLift}
              min={0} max={50}
              hint="Campaign reach as % of audience. Each 1% reach drives ~0.4% additional demand (diminishing returns not modelled)."
            />

            <UniSlider
              label="New Revenue Streams"
              value={newStreams}
              onChange={setNewStreams}
              min={0} max={50}
              hint="Revenue from new product lines or markets, added as a % of baseline revenue (additive, independent of volume/price)."
            />
          </div>
        </div>

        {/* Right: Live results */}
        <div className="lg:col-span-2 space-y-4">
          {loading ? (
            <div className="space-y-3">
              {[1,2,3].map(i => <div key={i} className="skeleton h-24 rounded-lg" />)}
            </div>
          ) : sim && hasAnyParam ? (
            <>
              {/* Headline delta */}
              <div className={`card p-4 border-l-[3px] ${sim.delta.revPct >= 0 ? 'border-l-green-500' : 'border-l-red-500'}`}>
                <div className="section-label mb-1">{scenarioName}</div>
                <div className="flex items-end gap-2 mt-1">
                  {sim.delta.revPct >= 0
                    ? <TrendingUp className="w-5 h-5 text-success mb-0.5 flex-shrink-0" />
                    : <TrendingDown className="w-5 h-5 text-danger mb-0.5 flex-shrink-0" />
                  }
                  <div>
                    <div className={`text-2xl font-bold tabular-nums ${sim.delta.revPct >= 0 ? 'text-success' : 'text-danger'}`}>
                      {sim.delta.revPct >= 0 ? '+' : ''}{formatCurrency(Math.abs(sim.delta.revenue))}
                    </div>
                    <div className={`text-xs font-semibold ${sim.delta.revPct >= 0 ? 'text-success' : 'text-danger'}`}>
                      {sim.delta.revPct >= 0 ? '+' : ''}{sim.delta.revPct.toFixed(1)}% vs baseline
                    </div>
                  </div>
                </div>
              </div>

              {/* Comparison bars */}
              <div className="card p-4 space-y-5">
                <div className="section-label">Baseline vs Scenario</div>
                <DeltaBar
                  label="Revenue"
                  base={sim.base.revenue}
                  scenario={sim.scenario.revenue}
                  fmt={v => formatCurrency(v)}
                />
                <DeltaBar
                  label="Orders"
                  base={sim.base.orders}
                  scenario={sim.scenario.orders}
                  fmt={v => v.toLocaleString()}
                />
                <DeltaBar
                  label="Avg. Order Value"
                  base={sim.base.aov}
                  scenario={sim.scenario.aov}
                  fmt={v => formatCurrency(v)}
                />
              </div>

              {/* Revenue breakdown */}
              {sim.breakdown.addl > 0 && (
                <div className="card p-4 space-y-2">
                  <div className="section-label mb-2">Revenue Breakdown</div>
                  <div className="flex justify-between text-xs">
                    <span className="text-text-muted">Core (price × volume)</span>
                    <span className="tabular-nums font-semibold text-text">{formatCurrency(sim.breakdown.core)}</span>
                  </div>
                  <div className="flex justify-between text-xs">
                    <span className="text-text-muted">New streams (additive)</span>
                    <span className="tabular-nums font-semibold text-success">+{formatCurrency(sim.breakdown.addl)}</span>
                  </div>
                  <div className="flex justify-between text-xs border-t border-border pt-2 mt-1">
                    <span className="font-semibold text-text">Total Estimated</span>
                    <span className="tabular-nums font-bold text-text">{formatCurrency(sim.scenario.revenue)}</span>
                  </div>
                </div>
              )}

              <p className="text-[10px] text-text-dim px-1">
                SIMULATION · Simplified model · Results update live · Real outcomes may differ
              </p>
            </>
          ) : (
            <div className="card p-6 text-center">
              <FlaskConical className="w-10 h-10 text-text-dim mx-auto mb-3" />
              <div className="text-sm font-medium text-text-muted mb-1">Adjust parameters</div>
              <div className="text-xs text-text-dim">
                Move any slider to see the estimated outcome live — no button needed.
              </div>
              {sim && (
                <div className="mt-4 pt-4 border-t border-border space-y-1 text-xs text-text-muted">
                  <div className="flex justify-between">
                    <span>Current Revenue</span>
                    <span className="font-semibold tabular-nums text-text">{formatCurrency(sim.base.revenue)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Current Orders</span>
                    <span className="font-semibold tabular-nums text-text">{sim.base.orders.toLocaleString()}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Avg. Order Value</span>
                    <span className="font-semibold tabular-nums text-text">{formatCurrency(sim.base.aov)}</span>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
