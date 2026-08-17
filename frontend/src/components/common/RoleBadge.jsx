import React from 'react'

export const RoleBadge = ({ role }) => {
  const normalized = (role || 'viewer').toLowerCase()

  const styles = {
    admin: 'bg-[#16233b] text-[#7fb6ff] border-[#2c4d85]/40',
    manager: 'bg-secondary/15 text-secondary border-secondary/30',
    viewer: 'bg-slate-100 text-slate-600 border-slate-200',
  }

  const roleLabels = {
    admin: 'Admin',
    manager: 'Manager',
    viewer: 'Viewer',
  }

  return (
    <span
      className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded text-[10.5px] font-bold tracking-wider uppercase border ${
        styles[normalized] || styles.viewer
      }`}
    >
      <span className="w-1.5 h-1.5 rounded-full bg-current"></span>
      {roleLabels[normalized] || role}
    </span>
  )
}
