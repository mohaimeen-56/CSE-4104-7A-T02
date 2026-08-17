import React from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { CsvDropzone } from '../components/sales/CsvDropzone'
import { ChevronRight } from 'lucide-react'

export const CsvUpload = () => {
  const navigate = useNavigate()

  return (
    <div className="space-y-4 max-w-3xl">
      {/* Breadcrumb matching mockup */}
      <div className="flex items-center gap-1.5 text-xs font-semibold text-text-muted">
        <Link to="/sales" className="hover:text-primary transition-colors">
          Sales Records
        </Link>
        <ChevronRight className="w-3.5 h-3.5" />
        <span className="text-primary">Upload CSV</span>
      </div>

      <div>
        <h1 className="text-xl font-bold text-text tracking-tight">
          Upload Sales Data
        </h1>
        <p className="text-xs text-text-muted mt-0.5">
          Bulk import your sales transactions using standard CSV formatting
        </p>
      </div>

      <div className="bg-surface border border-border rounded-2xl p-6 sm:p-7 shadow-sm">
        <CsvDropzone
          onUploadSuccess={() => {
            setTimeout(() => {
              // Option to stay or navigate
            }, 3000)
          }}
        />
      </div>
    </div>
  )
}
