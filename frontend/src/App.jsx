import { Routes, Route } from 'react-router-dom'
import Layout from './components/Layout.jsx'
import Dashboard from './pages/Dashboard.jsx'
import ActionsList from './pages/actions/List.jsx'
import ActionCreate from './pages/actions/Create.jsx'
import ActionDetail from './pages/actions/Detail.jsx'
import PlansIndex from './pages/plans/Index.jsx'
import AdminIndex from './pages/admin/Index.jsx'

function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/actions" element={<ActionsList />} />
        <Route path="/actions/new" element={<ActionCreate />} />
        <Route path="/actions/:actId" element={<ActionDetail />} />
        <Route path="/plans" element={<PlansIndex />} />
        <Route path="/admin" element={<AdminIndex />} />
      </Routes>
    </Layout>
  )
}

export default App
