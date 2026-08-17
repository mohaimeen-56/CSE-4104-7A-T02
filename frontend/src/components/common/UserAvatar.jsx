import React from 'react'
import { getInitials } from '../../utils/formatters'

export const UserAvatar = ({ name, size = 'md', className = '' }) => {
  const initials = getInitials(name)

  const sizeClasses = {
    sm: 'w-7 h-7 text-xs',
    md: 'w-8 h-8 text-xs',
    lg: 'w-10 h-10 text-sm font-bold',
    xl: 'w-16 h-16 text-xl font-bold',
  }

  return (
    <div
      className={`rounded-full bg-secondary text-white font-semibold flex items-center justify-center shadow-sm select-none ${
        sizeClasses[size] || sizeClasses.md
      } ${className}`}
      title={name || 'User'}
    >
      {initials}
    </div>
  )
}
