import React, { useState, useEffect, useCallback } from 'react'
import { Outlet } from 'react-router-dom'
import { Sidebar } from './Sidebar'
import { TopNavbar } from './TopNavbar'
import { CommandBar } from '../components/common/CommandBar'

export const AppShell = () => {
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [commandOpen, setCommandOpen] = useState(false)

  const openCommand = useCallback(() => setCommandOpen(true), [])
  const closeCommand = useCallback(() => setCommandOpen(false), [])

  // Global keyboard shortcut Ctrl+K / Cmd+K
  useEffect(() => {
    const handler = (e) => {
      if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault()
        setCommandOpen(prev => !prev)
      }
    }
    window.addEventListener('keydown', handler)
    return () => window.removeEventListener('keydown', handler)
  }, [])

  return (
    <div className="flex h-screen w-screen overflow-hidden bg-bg">
      <Sidebar
        isOpen={sidebarOpen}
        onClose={() => setSidebarOpen(false)}
        onOpenCommand={openCommand}
      />

      <div className="flex-1 flex flex-col min-w-0 h-full overflow-hidden">
        <TopNavbar
          onToggleSidebar={() => setSidebarOpen(true)}
          onOpenCommand={openCommand}
        />
        <main className="flex-1 overflow-y-auto px-5 py-5 lg:px-7 lg:py-6">
          <Outlet />
        </main>
      </div>

      <CommandBar isOpen={commandOpen} onClose={closeCommand} />
    </div>
  )
}
