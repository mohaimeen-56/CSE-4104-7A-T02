import React from 'react'
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  Cell,
} from 'recharts'
import { formatCurrency } from '../../utils/formatters'

export const ProductBarChart = ({ data = [], onBarClick, activeProductId }) => {
  if (!data || data.length === 0) {
    return (
      <div className="h-44 flex items-center justify-center text-text-muted text-xs">
        No product data available
      </div>
    )
  }

  const chartData = data.slice(0, 5).map((item) => ({
    id: item.product_id,
    name: item.product_name || item.name,
    units: item.units_sold || item.units,
    revenue: item.revenue,
  }))

  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-surface p-2.5 px-3 border border-border rounded-lg shadow-lg text-xs">
          <p className="font-bold text-primary mb-1">{label}</p>
          <p className="text-text-muted">
            Units Sold: <span className="font-semibold text-text">{payload[0].value}</span>
          </p>
          <p className="font-mono text-secondary font-semibold mt-0.5">
            {formatCurrency(payload[0].payload.revenue)}
          </p>
        </div>
      )
    }
    return null
  }

  return (
    <div className="w-full h-44 sm:h-48 pt-2">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#E3E7EC" />
          <XAxis
            dataKey="name"
            stroke="#6B7280"
            fontSize={10.5}
            tickLine={false}
            interval={0}
            tickFormatter={(val) => (val.length > 8 ? `${val.slice(0, 7)}…` : val)}
          />
          <YAxis stroke="#6B7280" fontSize={11} tickLine={false} />
          <Tooltip content={<CustomTooltip />} />
          <Bar
            dataKey="units"
            radius={[5, 5, 2, 2]}
            onClick={(entry) => onBarClick && onBarClick(entry.id)}
            cursor={onBarClick ? 'pointer' : 'default'}
          >
            {chartData.map((entry, index) => (
              <Cell
                key={`cell-${index}`}
                fill={index === 1 ? '#1F3864' : '#3B6FA8'}
                opacity={activeProductId && activeProductId !== entry.id ? 0.35 : 1}
              />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}
