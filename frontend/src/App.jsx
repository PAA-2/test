import { Routes, Route } from 'react-router-dom'
import Layout from './components/Layout.jsx'
import ProtectedRoute from './components/ProtectedRoute.jsx'
import Dashboard from './pages/Dashboard.jsx'
import ActionsList from './pages/actions/List.jsx'
import ActionCreate from './pages/actions/Create.jsx'
import ActionDetail from './pages/actions/Detail.jsx'
import PlansIndex from './pages/plans/Index.jsx'
import AdminIndex from './pages/admin/Index.jsx'
import Login from './pages/auth/Login.jsx'

function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route element={<ProtectedRoute><Layout /></ProtectedRoute>}>
        <Route path="/" element={<Dashboard />} />
        <Route path="/actions" element={<ActionsList />} />
        <Route path="/actions/new" element={<ActionCreate />} />
        <Route path="/actions/:actId" element={<ActionDetail />} />
        <Route path="/plans" element={<PlansIndex />} />
        <Route path="/admin" element={<AdminIndex />} />
      </Route>
    </Routes>
  )
}

export default App
