import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Layout from '@/components/layout/Layout';

import GraphPage from '@/pages/Graph';

import Dashboard from '@/pages/Dashboard';

// Placeholder Pages
// Recommend component removed as it was unused

import RecommendPage from '@/pages/Recommend';
import LinchpinsPage from '@/pages/Linchpins';

function App() {
  return (
    <Router>
      <Layout>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/recommend" element={<RecommendPage />} />
          <Route path="/graph" element={<GraphPage />} />
          <Route path="/linchpins" element={<LinchpinsPage />} />
        </Routes>
      </Layout>
    </Router>
  );
}

export default App;
