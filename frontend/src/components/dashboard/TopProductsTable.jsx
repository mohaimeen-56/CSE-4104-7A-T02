import React from 'react'
import { formatCurrency, formatNumber } from '../../utils/formatters'

export const TopProductsTable = ({ products = [] }) => {
  if (!products || products.length === 0) {
    return (
      <div className="p-8 text-center text-text-muted text-xs">
        No top product records available
      </div>
    )
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-left text-xs border-collapse">
        <thead>
          <tr className="border-b border-border text-[10.5px] uppercase tracking-wider text-text-muted font-bold">
            <th className="py-2.5 px-3 w-10">#</th>
            <th className="py-2.5 px-3">Product</th>
            <th className="py-2.5 px-3">Category</th>
            <th className="py-2.5 px-3 text-right">Units</th>
            <th className="py-2.5 px-3 text-right">Revenue</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-border font-medium">
          {products.map((p, idx) => (
            <tr key={p.product_id || idx} className="hover:bg-slate-50 transition-colors">
              <td className="py-3 px-3">
                <span className="inline-flex items-center justify-center w-5 h-5 rounded bg-[#EAF1F8] text-primary font-bold font-mono text-[11px]">
                  {p.rank || idx + 1}
                </span>
              </td>
              <td className="py-3 px-3 font-semibold text-text">{p.product_name}</td>
              <td className="py-3 px-3 text-text-muted">{p.category || 'General'}</td>
              <td className="py-3 px-3 text-right font-mono font-semibold text-text">
                {formatNumber(p.units_sold)}
              </td>
              <td className="py-3 px-3 text-right font-mono font-semibold text-primary">
                {formatCurrency(p.revenue)}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
