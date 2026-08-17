import React from 'react'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider, useAuth } from './context/AuthContext'
import { NotificationProvider } from './context/NotificationContext'
import { MaintenanceProvider, useMaintenance } from './context/MaintenanceContext'
import { AppShell } from './layouts/AppShell'
import { MaintenanceScreen } from './components/common/MaintenanceScreen'

// Pages
import { Login } from './pages/Login'
import { Register } from './pages/Register'
import { Dashboard } from './pages/Dashboard'
import { SalesRecords } from './pages/SalesRecords'
import { CsvUpload } from './pages/CsvUpload'
import { AIInsights } from './pages/AIInsights'
import { AIChatbot } from './pages/AIChatbot'
import { Reports } from './pages/Reports'
import { Settings } from './pages/Settings'
import { NotFound } from './pages/NotFound'
// Phase 3 pages
import { Intelligence } from './pages/Intelligence'
import { DataExplorer } from './pages/DataExplorer'
import { ForecastPage } from './pages/ForecastPage'
import { ScenarioLab } from './pages/ScenarioLab'
import { AnomaliesPage } from './pages/AnomaliesPage'
import { Notifications } from './pages/Notifications'

const ProtectedRoute = ({ children, allowedRoles }) => {
  const { isAuthenticated, user, loading } = useAuth()
  const { status: maintenanceStatus } = useMaintenance()

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-bg">
        <div className="flex items-center gap-2 text-xs font-semibold text-text-muted">
          <div className="w-4 h-4 border-2 border-secondary/30 border-t-secondary rounded-full animate-spin" />
          Loading session…
        </div>
      </div>
    )
  }

  if (!isAuthenticated) return <Navigate to="/login" replace />

  if (maintenanceStatus?.enabled && user?.role !== 'admin') {
    return <MaintenanceScreen status={maintenanceStatus} />
  }

  if (allowedRoles && allowedRoles.length > 0 && !allowedRoles.includes(user?.role)) {
    return <Navigate to="/dashboard" replace />
  }

  return children
}

const PublicRoute = ({ children }) => {
  const { isAuthenticated, loading } = useAuth()
  if (loading) return null
  if (isAuthenticated) return <Navigate to="/dashboard" replace />
  return children
}

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <MaintenanceProvider>
          <NotificationProvider>
            <Routes>
              {/* Public */}
              <Route path="/login" element={<PublicRoute><Login /></PublicRoute>} />
              <Route path="/register" element={<PublicRoute><Register /></PublicRoute>} />

              {/* Protected App */}
              <Route path="/" element={<ProtectedRoute><AppShell /></ProtectedRoute>}>
                <Route index element={<Navigate to="/dashboard" replace />} />
                <Route path="dashboard" element={<Dashboard />} />

                {/* Analytics */}
                <Route path="explorer" element={<DataExplorer />} />
                <Route path="sales" element={<SalesRecords />} />
                <Route path="sales/upload" element={
                  <ProtectedRoute allowedRoles={['admin', 'manager']}>
                    <CsvUpload />
                  </ProtectedRoute>
                } />

                {/* Intelligence */}
                <Route path="insights" element={<AIInsights />} />
                <Route path="forecast" element={<ForecastPage />} />
                <Route path="anomalies" element={<AnomaliesPage />} />
                <Route path="chatbot" element={<AIChatbot />} />

                {/* Decision Support */}
                <Route path="scenarios" element={<ScenarioLab />} />
                <Route path="intelligence" element={<Intelligence />} />

                {/* Reporting */}
                <Route path="reports" element={<Reports />} />

                {/* System */}
                <Route path="notifications" element={<Notifications />} />
                <Route path="settings" element={<Settings />} />
              </Route>

              <Route path="*" element={<NotFound />} />
            </Routes>
          </NotificationProvider>
        </MaintenanceProvider>
      </AuthProvider>
    </BrowserRouter>
  )
}
