import { BrowserRouter, Routes, Route, Link } from 'react-router-dom'
import SubmitPage from './pages/SubmitPage'
import JobListPage from './pages/JobListPage'
import JobDetailPage from './pages/JobDetailPage'

function NavBar() {
  return (
    <nav className="bg-gray-900 border-b border-gray-800 px-6 py-3 flex items-center justify-between w-full">
      <Link to="/" className="font-bold text-lg tracking-tight text-white hover:text-gray-300 transition-colors">
        YT Pipeline
      </Link>
      <Link to="/jobs" className="text-sm text-gray-400 hover:text-white transition-colors">
        Jobs
      </Link>
    </nav>
  )
}

function App() {
  return (
    <BrowserRouter>
      <NavBar />
      <Routes>
        <Route path="/" element={<SubmitPage />} />
        <Route path="/jobs" element={<JobListPage />} />
        <Route path="/jobs/:id" element={<JobDetailPage />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App
