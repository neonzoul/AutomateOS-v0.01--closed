import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { Box } from '@chakra-ui/react';
import { LoginPage } from './components/auth/LoginPage';
import { ProtectedRoute } from './components/auth/ProtectedRoute';
import { Dashboard } from './components/dashboard/Dashboard';
import { WorkflowEditor } from './components/editor/WorkflowEditor';
import { WorkflowLogsPage } from './components/dashboard/WorkflowLogsPage';
import NodeDemo from './components/editor/NodeDemo';
import NodeTest from './components/editor/NodeTest';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/node-demo" element={<NodeDemo />} />
        <Route path="/node-test" element={<NodeTest />} />
        <Route
          path="/"
          element={
            <ProtectedRoute>
              <Dashboard />
            </ProtectedRoute>
          }
        />
        <Route
          path="/workflows/:id/edit"
          element={
            <ProtectedRoute>
              <WorkflowEditor />
            </ProtectedRoute>
          }
        />
        <Route
          path="/workflows/:id/logs"
          element={
            <ProtectedRoute>
              <WorkflowLogsPage />
            </ProtectedRoute>
          }
        />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
