import { Routes, Route } from 'react-router-dom';
import AppShell from './components/layout/AppShell';
import DashboardPage from './pages/DashboardPage';
import SearchPage from './pages/SearchPage';
import FilesPage from './pages/FilesPage';
import AskPage from './pages/AskPage';
import AgentPage from './pages/AgentPage';

function App() {
  return (
    <AppShell>
      <Routes>
        <Route path="/" element={<DashboardPage />} />
        <Route path="/search" element={<SearchPage />} />
        <Route path="/files" element={<FilesPage />} />
        <Route path="/ask" element={<AskPage />} />
        <Route path="/agent" element={<AgentPage />} />
      </Routes>
    </AppShell>
  );
}

export default App;
