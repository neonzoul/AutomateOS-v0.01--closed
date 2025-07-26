import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { Box } from '@chakra-ui/react';
import { LoginPage } from './components/auth/LoginPage';
import { ProtectedRoute } from './components/auth/ProtectedRoute';
import { Dashboard } from './components/dashboard/Dashboard';
import { WorkflowEditor } from './components/editor/WorkflowEditor';
import NodeDemo from './components/editor/NodeDemo';
import NodeTest from './components/editor/NodeTest';

function App() {
  return (
    <Box>
      <BrowserRouter>
        <Routes>
          {/* Public Route */}
          <Route path="/login" element={<LoginPage />} />
          <Route path="/test-nodes" element={<NodeDemo />} />
          <Route path="/node-test" element={<NodeTest />} />

          {/* Protected Routes */}
          <Route element={<ProtectedRoute />}>
            <Route path="/" element={<Dashboard />} />
            <Route path="/workflows/new" element={<WorkflowEditor />} />
            <Route path="/workflows/:id/edit" element={<WorkflowEditor />} />
            <Route path="/node-demo" element={<NodeDemo />} />
            {/* Add other protected routes here later */}
          </Route>
        </Routes>
      </BrowserRouter>
    </Box>
  );
}

export default App;