import React from 'react'
import { ResponsiveContainer, PieChart, Pie, Cell, Tooltip } from 'recharts'
import { formatCurrency } from '../../utils/formatters'

const REGION_COLORS = ['#1F3864', '#2E86AB', '#E0A800', '#2E7D32', '#C0392B']

export const RegionDonutChart = ({ data = [], onSliceClick, activeRegionId }) => {
  if (!data || data.length === 0) {
    return (
      <div className="h-44 flex items-center justify-center text-text-muted text-xs">
        No regional sales data available
      </div>
    )
  }

  const chartData = data.map((item) => ({
    id: item.region_id,
    name: item.region_name || item.name,
    value: item.revenue,
    percentage: item.percentage,
    units: item.units_sold || item.units,
  }))

  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      const { name, value, percentage, units } = payload[0].payload
      return (
        <div className="bg-surface p-2.5 px-3 border border-border rounded-lg shadow-lg text-xs">
          <p className="font-bold text-primary mb-1">{name}</p>
          <p className="font-mono text-secondary font-semibold">
            {formatCurrency(value)} ({percentage}%)
          </p>
          {units !== undefined && (
            <p className="text-text-muted text-[11px] mt-0.5">Units: {units}</p>
          )}
        </div>
      )
    }
    return null
  }

  return (
    <div className="flex flex-col sm:flex-row items-center justify-around gap-4 h-44 sm:h-48 pt-2">
      <div className="w-28 h-28 sm:w-32 sm:h-32 flex-shrink-0">
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Tooltip content={<CustomTooltip />} />
            <Pie
              data={chartData}
              innerRadius="62%"
              outerRadius="90%"
              paddingAngle={3}
              dataKey="value"
              onClick={(entry) => onSliceClick && onSliceClick(entry.id)}
              cursor={onSliceClick ? 'pointer' : 'default'}
            >
              {chartData.map((entry, index) => (
                <Cell
                  key={`cell-${index}`}
                  fill={REGION_COLORS[index % REGION_COLORS.length]}
                  opacity={activeRegionId && activeRegionId !== entry.id ? 0.35 : 1}
                />
              ))}
            </Pie>
          </PieChart>
        </ResponsiveContainer>
      </div>

      <div className="flex flex-col gap-1.5 text-xs w-full max-w-[200px]">
        {chartData.map((item, idx) => (
          <div
            key={item.name}
            onClick={() => onSliceClick && onSliceClick(item.id)}
            className={`flex items-center justify-between gap-2 ${onSliceClick ? 'cursor-pointer hover:opacity-80' : ''} ${activeRegionId && activeRegionId !== item.id ? 'opacity-40' : ''}`}
          >
            <div className="flex items-center gap-2 truncate">
              <span
                className="w-2.5 h-2.5 rounded-sm flex-shrink-0"
                style={{ backgroundColor: REGION_COLORS[idx % REGION_COLORS.length] }}
              />
              <span className="text-text truncate font-medium">{item.name}</span>
            </div>
            <span className="font-mono font-bold text-text ml-auto">
              {item.percentage}%
            </span>
          </div>
        ))}
      </div>
    </div>
  )
}
