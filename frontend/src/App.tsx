import { Routes, Route, Navigate } from 'react-router-dom';
import MainLayout from './layouts/MainLayout';
import Dashboard from './pages/Dashboard';
import DocParser from './pages/DocParser';
import DemandForecast from './pages/DemandForecast';
import AIAgent from './pages/AIAgent';
import RiskControl from './pages/RiskControl';
import ChatBI from './pages/ChatBI';
import ReportPreview from './pages/ReportPreview';

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<MainLayout />}>
        <Route index element={<Navigate to="/dashboard" replace />} />
        <Route path="dashboard" element={<Dashboard />} />
        <Route path="doc-parser" element={<DocParser />} />
        <Route path="demand-forecast" element={<DemandForecast />} />
        <Route path="ai-agent" element={<AIAgent />} />
        <Route path="risk-control" element={<RiskControl />} />
        <Route path="chatbi" element={<ChatBI />} />
        <Route path="report" element={<ReportPreview />} />
      </Route>
    </Routes>
  );
}
