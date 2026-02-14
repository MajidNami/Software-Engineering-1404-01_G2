import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import MainLayout from '@/components/layouts/MainLayout';
import HomePage from '@/pages/HomePage';
import SuggestDestination from './pages/SuggestDestination';
import CreateTrip from './pages/CreateTrip';
import FinalizeTrip from './pages/FinalizeTrip';
import Login from './pages/Login';
import Signup from './pages/Signup';
import Trips from './pages/Trips';
import ScrollToTop from './components/ScrollToTop';
import { NotificationProvider } from '@/contexts/NotificationContext';
import NotificationContainer from '@/components/ui/NotificationContainer';


function App() {
  return (
    <NotificationProvider>
      <Router basename="/team11">
        <ScrollToTop />
        <NotificationContainer />
        <Routes>
          {/* Auth Routes (without MainLayout) */}
          <Route path="/login" element={<Login />} />
          <Route path="/signup" element={<Signup />} />

          {/* Main Application Shell */}
          <Route path="/" element={<MainLayout />}>
            <Route index element={<HomePage />} />
            <Route path="create-trip" element={<CreateTrip />} />
            <Route path="suggest-destination" element={<SuggestDestination />} />
            <Route path="trip-details/:tripId" element={<FinalizeTrip />} />
            <Route path="trips" element={<Trips />} />
          </Route>

          {/* Catch-all redirect to home */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </Router>
    </NotificationProvider>
  );
}

export default App;