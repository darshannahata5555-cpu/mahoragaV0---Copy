import { BrowserRouter, Routes, Route } from 'react-router-dom'
import SubmitPage from './pages/SubmitPage'
import JobListPage from './pages/JobListPage'
import JobDetailPage from './pages/JobDetailPage'

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<SubmitPage />} />
        <Route path="/jobs" element={<JobListPage />} />
        <Route path="/jobs/:id" element={<JobDetailPage />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App
