import React from 'react'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { Layout } from './components/layout/Layout'
import { Dashboard } from './pages/Dashboard'
import { PlacementAnalysis } from './pages/PlacementAnalysis'
import { Applications } from './pages/Applications'
import { InterviewPrep } from './pages/InterviewPrep'
import { ActionCenter } from './pages/ActionCenter'
import { Settings } from './pages/Settings'

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Dashboard />} />
          <Route path="placement-analysis" element={<PlacementAnalysis />} />
          <Route path="applications" element={<Applications />} />
          <Route path="interview-prep" element={<InterviewPrep />} />
          <Route path="action-center" element={<ActionCenter />} />
          <Route path="settings" element={<Settings />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}

export default App
