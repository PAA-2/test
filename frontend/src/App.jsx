import { Routes, Route } from 'react-router-dom'
import Layout from './components/Layout.jsx'
import ProtectedRoute from './components/ProtectedRoute.jsx'
import Dashboard from './pages/Dashboard.jsx'
import ActionsList from './pages/actions/List.jsx'
import ActionCreate from './pages/actions/Create.jsx'
import ActionDetail from './pages/actions/Detail.jsx'
import ActionEdit from './pages/actions/Edit.jsx'
import Assistant from './pages/actions/Assistant.jsx'
import PlansIndex from './pages/plans/Index.jsx'
import PlanEdit from './pages/plans/Edit.jsx'
import AdminIndex from './pages/admin/Index.jsx'
import CustomFieldsList from './pages/admin/custom-fields/List.jsx'
import CustomFieldEdit from './pages/admin/custom-fields/Edit.jsx'
import TemplatesList from './pages/admin/templates/List.jsx'
import TemplateEdit from './pages/admin/templates/Edit.jsx'
import AutomationsList from './pages/admin/automations/List.jsx'
import AutomationEdit from './pages/admin/automations/Edit.jsx'
import MenusList from './pages/admin/menus/List.jsx'
import Login from './pages/auth/Login.jsx'
import Forbidden403 from './pages/errors/Forbidden403.jsx'
import ReportsCustom from './pages/reports/Custom.jsx'
import QualityIndex from './pages/quality/Index.jsx'

function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route element={<ProtectedRoute><Layout /></ProtectedRoute>}>
        <Route path="/" element={<Dashboard />} />
        <Route path="/actions" element={<ActionsList />} />
        <Route path="/actions/new" element={<ActionCreate />} />
        <Route path="/actions/assistant" element={<Assistant />} />
        <Route path="/actions/:actId" element={<ActionDetail />} />
        <Route path="/actions/:actId/edit" element={<ActionEdit />} />
        <Route path="/plans" element={<ProtectedRoute><PlansIndex /></ProtectedRoute>} />
        <Route
          path="/plans/new"
          element={<ProtectedRoute roles={['SuperAdmin', 'PiloteProcessus']}><PlanEdit /></ProtectedRoute>}
        />
        <Route
          path="/plans/:planId/edit"
          element={<ProtectedRoute roles={['SuperAdmin', 'PiloteProcessus']}><PlanEdit /></ProtectedRoute>}
        />
        <Route
          path="/reports/custom"
          element={<ProtectedRoute roles={['SuperAdmin', 'PiloteProcessus', 'Pilote']}><ReportsCustom /></ProtectedRoute>}
        />
        <Route
          path="/quality"
          element={<ProtectedRoute roles={['SuperAdmin', 'PiloteProcessus', 'Pilote']}><QualityIndex /></ProtectedRoute>}
        />
        <Route
          path="/admin"
          element={<ProtectedRoute roles={['SuperAdmin']}><AdminIndex /></ProtectedRoute>}
        />
        <Route
          path="/admin/templates"
          element={<ProtectedRoute roles={['SuperAdmin', 'PiloteProcessus']}><TemplatesList /></ProtectedRoute>}
        />
        <Route
          path="/admin/templates/new"
          element={<ProtectedRoute roles={['SuperAdmin', 'PiloteProcessus']}><TemplateEdit /></ProtectedRoute>}
        />
        <Route
          path="/admin/templates/:id"
          element={<ProtectedRoute roles={['SuperAdmin', 'PiloteProcessus']}><TemplateEdit /></ProtectedRoute>}
        />
        <Route
          path="/admin/automations"
          element={<ProtectedRoute roles={['SuperAdmin', 'PiloteProcessus']}><AutomationsList /></ProtectedRoute>}
        />
        <Route
          path="/admin/automations/new"
          element={<ProtectedRoute roles={['SuperAdmin', 'PiloteProcessus']}><AutomationEdit /></ProtectedRoute>}
        />
        <Route
          path="/admin/automations/:id"
          element={<ProtectedRoute roles={['SuperAdmin', 'PiloteProcessus']}><AutomationEdit /></ProtectedRoute>}
        />
        <Route
          path="/admin/menus"
          element={<ProtectedRoute roles={['SuperAdmin', 'PiloteProcessus']}><MenusList /></ProtectedRoute>}
        />
        <Route
          path="/admin/custom-fields"
          element={<ProtectedRoute roles={['SuperAdmin', 'PiloteProcessus']}><CustomFieldsList /></ProtectedRoute>}
        />
        <Route
          path="/admin/custom-fields/new"
          element={<ProtectedRoute roles={['SuperAdmin', 'PiloteProcessus']}><CustomFieldEdit /></ProtectedRoute>}
        />
        <Route
          path="/admin/custom-fields/:id"
          element={<ProtectedRoute roles={['SuperAdmin', 'PiloteProcessus']}><CustomFieldEdit /></ProtectedRoute>}
        />
      </Route>
      <Route path="/403" element={<Forbidden403 />} />
    </Routes>
  )
}

export default App
