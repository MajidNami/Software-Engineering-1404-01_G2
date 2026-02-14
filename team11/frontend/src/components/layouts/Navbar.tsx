import { Link, useNavigate } from 'react-router-dom';
import Button from '../ui/Button';
import { useAuth } from '@/context/AuthContext';

const Navbar = () => {
  const { isAuthenticated, user, logout, isLoading } = useAuth();
  const navigate = useNavigate();

  const handleLogout = async () => {
    await logout();
    navigate('/');
  };

  return (
    <header className="main-header">
      <div className="container header-content">
        {/* Right Side: Branding from your HTML */}
        <Link to="http://localhost:8000/" className="logo no-underline">
          <i className="fa-solid fa-leaf text-persian-gold text-3xl"></i>
          <div className="logo-text">
            <h1 className="text-xl font-extrabold text-white">ایران‌نما</h1>
            <span className="text-xs text-white">سامانه هوشمند گردشگری</span>
          </div>
        </Link>

        {/* Group 11 Specific Badge */}
        <div className="hidden md:flex items-center px-4 py-1 rounded-full bg-white/10 border border-white/20"
          style={{
            position: 'absolute',
            left: '50%',
            transform: 'translate(-50%,0)'
          }}>
          <Link to="/">
            <span className="p-2 text-white text-sm font-bold" >سرویس برنامه‌ریزی سفر (گروه ۱۱)</span>
          </Link>
        </div>

        {/* Left Side: Auth & Team Identity */}
        <div className="flex items-center gap-6">
          {!isLoading && (
            <div className="auth-buttons flex gap-2">
              {isAuthenticated ? (
                <>
                  {user && (
                    <span className="text-white text-sm px-3 py-2 hidden md:block">
                      {user.first_name || user.email}
                    </span>
                  )}
                  <Link to="/trips">
                    <Button variant="secondary" className="px-5 py-2 text-sm">
                      سفرها
                    </Button>
                  </Link>
                  <Button
                    variant="secondary"
                    className="px-5 py-2 text-sm"
                    onClick={handleLogout}
                  >
                    خروج
                  </Button>
                </>
              ) : (
                <>
                  <Link to="/login">
                    <Button variant="secondary" className="px-5 py-2 text-sm">ورود</Button>
                  </Link>
                  <Link to="/signup">
                    <Button variant="secondary" className="px-5 py-2 text-sm">ثبت‌نام</Button>
                  </Link>
                </>
              )}
            </div>
          )}
        </div>
      </div>
    </header>
  );
};

export default Navbar;