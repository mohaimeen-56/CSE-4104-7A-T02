import React, { useState, useRef } from 'react'
import { UploadCloud, FileText, CheckCircle2, AlertTriangle, X } from 'lucide-react'
import { salesApi } from '../../services/api'

export const CsvDropzone = ({ onUploadSuccess }) => {
  const [file, setFile] = useState(null)
  const [isDragging, setIsDragging] = useState(false)
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState('')
  const fileInputRef = useRef(null)

  const handleDragOver = (e) => {
    e.preventDefault()
    setIsDragging(true)
  }

  const handleDragLeave = () => {
    setIsDragging(false)
  }

  const handleDrop = (e) => {
    e.preventDefault()
    setIsDragging(false)
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      validateAndSetFile(e.dataTransfer.files[0])
    }
  }

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      validateAndSetFile(e.target.files[0])
    }
  }

  const validateAndSetFile = (f) => {
    setError('')
    setResult(null)
    if (!f.name.toLowerCase().endsWith('.csv')) {
      setError('Please select a valid CSV (.csv) file.')
      return
    }
    setFile(f)
  }

  const handleUpload = async () => {
    if (!file || loading) return
    setLoading(true)
    setError('')
    setResult(null)

    const formData = new FormData()
    formData.append('file', file)

    try {
      const res = await salesApi.uploadCsv(formData)
      setResult(res.data)
      if (onUploadSuccess) onUploadSuccess(res.data)
    } catch (err) {
      setError(err.message || 'Failed to upload CSV file.')
    } finally {
      setLoading(false)
    }
  }

  const clearFile = () => {
    setFile(null)
    setResult(null)
    setError('')
    if (fileInputRef.current) fileInputRef.current.value = ''
  }

  return (
    <div className="space-y-4">
      <div
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
        className={`border-2 border-dashed rounded-2xl p-10 text-center cursor-pointer transition-all bg-white ${
          isDragging
            ? 'border-secondary bg-secondary/5'
            : 'border-[#C3CFDE] hover:border-secondary/60'
        }`}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept=".csv"
          onChange={handleFileChange}
          className="hidden"
        />
        <div className="flex flex-col items-center">
          <UploadCloud className="w-12 h-12 text-secondary mb-3 stroke-[1.5]" />
          <h4 className="font-bold text-base text-text mb-1">
            {file ? file.name : 'Drag & drop your CSV file here'}
          </h4>
          <p className="text-xs text-text-muted">
            {file
              ? `${(file.size / 1024).toFixed(1)} KB — Click to choose a different file`
              : 'or click to browse from your computer'}
          </p>
        </div>
      </div>

      <div className="bg-[#F8FAFC] border border-border rounded-xl p-4">
        <div className="text-[11.5px] font-bold text-text-muted uppercase tracking-wider mb-2">
          Required Columns
        </div>
        <div className="flex flex-wrap gap-2">
          {['product_id', 'region_id', 'quantity', 'unit_price', 'sale_date'].map((col) => (
            <code
              key={col}
              className="font-mono text-xs bg-white border border-border px-2.5 py-1 rounded-md text-primary font-semibold"
            >
              {col}
            </code>
          ))}
        </div>
        <div className="text-[11.5px] font-bold text-text-muted uppercase tracking-wider mt-3 mb-2">
          Optional Column
        </div>
        <div className="flex flex-wrap gap-2">
          <code className="font-mono text-xs bg-white border border-border px-2.5 py-1 rounded-md text-secondary font-semibold">
            sale_time
          </code>
        </div>
        <p className="text-[11px] text-text-muted mt-2">
          Format HH:MM or HH:MM:SS. Rows without a time use the server's current time-of-day and are flagged as estimated for data-quality reporting.
        </p>
      </div>

      {file && (
        <div className="flex items-center justify-between p-3 bg-surface border border-border rounded-xl">
          <div className="flex items-center gap-2 text-xs font-semibold text-text">
            <FileText className="w-4 h-4 text-secondary" />
            <span>{file.name}</span>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={clearFile}
              className="p-1 text-text-muted hover:text-danger rounded"
              title="Remove file"
            >
              <X className="w-4 h-4" />
            </button>
            <button
              onClick={handleUpload}
              disabled={loading}
              className="bg-primary hover:bg-primary-light disabled:opacity-50 text-white font-bold text-xs px-5 py-2 rounded-lg shadow-sm transition-colors"
            >
              {loading ? 'Processing…' : 'Upload File'}
            </button>
          </div>
        </div>
      )}

      {error && (
        <div className="p-4 bg-danger-bg border border-[#F3C7BD] text-danger rounded-xl text-xs flex items-center gap-2.5 font-semibold">
          <AlertTriangle className="w-4 h-4 flex-shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {result && (
        <div className="bg-surface border border-border rounded-xl p-5 space-y-3">
          <div className="flex items-center gap-2 text-success font-bold text-sm">
            <CheckCircle2 className="w-5 h-5" />
            <span>Upload Completed Successfully</span>
          </div>
          <div className="grid grid-cols-3 gap-3 text-center">
            <div className="p-3 bg-slate-50 rounded-lg">
              <div className="text-[11px] text-text-muted uppercase font-bold">Total Rows</div>
              <div className="font-mono text-lg font-bold text-text">{result.total_rows}</div>
            </div>
            <div className="p-3 bg-success-bg/60 rounded-lg">
              <div className="text-[11px] text-success uppercase font-bold">Imported</div>
              <div className="font-mono text-lg font-bold text-success">{result.imported_rows}</div>
            </div>
            <div className="p-3 bg-danger-bg/60 rounded-lg">
              <div className="text-[11px] text-danger uppercase font-bold">Failed</div>
              <div className="font-mono text-lg font-bold text-danger">{result.failed_rows}</div>
            </div>
          </div>

          {result.errors?.length > 0 && (
            <div className="mt-3">
              <div className="text-xs font-bold text-danger mb-1.5">Error details:</div>
              <div className="max-h-36 overflow-y-auto divide-y divide-border text-[11.5px] border border-border rounded-lg">
                {result.errors.map((err, i) => (
                  <div key={i} className="p-2 px-3 text-text-muted">
                    <strong className="text-danger">Row {err.row}:</strong> {err.message}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
