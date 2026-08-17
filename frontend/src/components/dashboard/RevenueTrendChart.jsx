import React from 'react'
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
} from 'recharts'
import { formatCurrency, formatCompact } from '../../utils/formatters'

export const RevenueTrendChart = ({ data = [] }) => {
  if (!data || data.length === 0) {
    return (
      <div className="h-44 flex items-center justify-center text-text-muted text-xs">
        No revenue trend data available
      </div>
    )
  }

  const chartData = data.map((item) => ({
    name: item.date,
    revenue: item.revenue,
    orders: item.orders,
  }))

  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-surface p-2.5 px-3 border border-border rounded-lg shadow-lg text-xs">
          <p className="font-bold text-primary mb-1">{label}</p>
          <p className="font-mono text-secondary font-semibold">
            Revenue: {formatCurrency(payload[0].value)}
          </p>
          {payload[0].payload.orders !== undefined && (
            <p className="text-text-muted text-[11px] mt-0.5">
              Orders: {payload[0].payload.orders}
            </p>
          )}
        </div>
      )
    }
    return null
  }

  return (
    <div className="w-full h-44 sm:h-48 pt-2">
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart data={chartData} margin={{ top: 10, right: 10, left: -15, bottom: 0 }}>
          <defs>
            <linearGradient id="colorRev" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#2E86AB" stopOpacity={0.4} />
              <stop offset="95%" stopColor="#2E86AB" stopOpacity={0.0} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#E3E7EC" />
          <XAxis
            dataKey="name"
            stroke="#6B7280"
            fontSize={11}
            tickLine={false}
            axisLine={{ stroke: '#E3E7EC' }}
          />
          <YAxis
            stroke="#6B7280"
            fontSize={11}
            tickLine={false}
            axisLine={{ stroke: '#E3E7EC' }}
            tickFormatter={(val) => `৳${formatCompact(val)}`}
          />
          <Tooltip content={<CustomTooltip />} />
          <Area
            type="monotone"
            dataKey="revenue"
            stroke="#1F3864"
            strokeWidth={3}
            fillOpacity={1}
            fill="url(#colorRev)"
            activeDot={false}
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  )
}
