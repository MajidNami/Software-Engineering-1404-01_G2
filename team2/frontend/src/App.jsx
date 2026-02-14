import { Routes, Route } from 'react-router-dom'
import Navbar from './components/Navbar'
import HomePage from './pages/HomePage'
import SearchPage from './pages/SearchPage'
import MyArticlePage from './pages/MyArticlePage'
import ArticlePage from './pages/ArticlePage'
import ManageArticlePage from './pages/ManageArticlePage'
import NewArticlePage from './pages/NewArticlePage'
import EditVersionPage from './pages/EditVersionPage'
import PreviewVersionPage from './pages/PreviewVersionPage'
import RequestPublishPage from './pages/RequestPublishPage'
import ReviewPublishPage from './pages/ReviewPublishPage'
import MyRequestsPage from './pages/MyRequestsPage'

export default function App() {
  return (
    <div className="min-h-screen bg-light text-dark">
      <Navbar />
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/search" element={<SearchPage />} />
        <Route path="/my-articles" element={<MyArticlePage />} />
        <Route path="/articles/new" element={<NewArticlePage />} />
        <Route path="/articles/:name" element={<ArticlePage />} />
        <Route path="/articles/:name/manage" element={<ManageArticlePage />} />
        <Route path="/articles/:name/requests" element={<RequestPublishPage />} />
        <Route path="/articles/:name/requests/:requestId/review" element={<ReviewPublishPage />} />
        <Route path="/articles/:name/my-requests" element={<MyRequestsPage />} />
        <Route path="/versions/:name/edit" element={<EditVersionPage />} />
        <Route path="/versions/:name/preview" element={<PreviewVersionPage />} />
      </Routes>
    </div>
  )
}
