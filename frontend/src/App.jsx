import { Routes, Route } from 'react-router-dom'
import Layout from './components/Layout.jsx'
import ProtectedRoute from './components/ProtectedRoute.jsx'
import Dashboard from './pages/Dashboard.jsx'
import ActionsList from './pages/actions/List.jsx'
import ActionCreate from './pages/actions/Create.jsx'
import ActionDetail from './pages/actions/Detail.jsx'
import PlansIndex from './pages/plans/Index.jsx'
import PlanEdit from './pages/plans/Edit.jsx'
import AdminIndex from './pages/admin/Index.jsx'
import Login from './pages/auth/Login.jsx'
import Forbidden403 from './pages/errors/Forbidden403.jsx'
import ReportsBuilder from './pages/reports/Builder.jsx'

function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route element={<ProtectedRoute><Layout /></ProtectedRoute>}>
        <Route path="/" element={<Dashboard />} />
        <Route path="/actions" element={<ActionsList />} />
        <Route path="/actions/new" element={<ActionCreate />} />
        <Route path="/actions/:actId" element={<ActionDetail />} />
        <Route
          path="/plans"
          element={<ProtectedRoute roles={['SuperAdmin', 'PiloteProcessus', 'Pilote']}><PlansIndex /></ProtectedRoute>}
        />
        <Route
          path="/plans/new"
          element={<ProtectedRoute roles={['SuperAdmin', 'PiloteProcessus']}><PlanEdit /></ProtectedRoute>}
        />
        <Route
          path="/plans/:planId/edit"
          element={<ProtectedRoute roles={['SuperAdmin', 'PiloteProcessus']}><PlanEdit /></ProtectedRoute>}
        />
        <Route
          path="/reports"
          element={<ProtectedRoute roles={['SuperAdmin', 'PiloteProcessus', 'Pilote']}><ReportsBuilder /></ProtectedRoute>}
        />
        <Route path="/admin" element={<ProtectedRoute roles={['SuperAdmin']}><AdminIndex /></ProtectedRoute>} />
      </Route>
      <Route path="/403" element={<Forbidden403 />} />
    </Routes>
  )
}

export default App
