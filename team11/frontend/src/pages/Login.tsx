import React from 'react';
import { useNavigate } from 'react-router-dom';
import LoginForm from '@/components/auth/LoginForm';
import { useNotification } from '@/contexts/NotificationContext';

const Login: React.FC = () => {
    const navigate = useNavigate();
    const { success } = useNotification();

    const handleSuccess = (user: any) => {
        success(`خوش آمدید ${user.first_name || user.email}`);
        navigate('/');
    };

    const handleSwitchToSignup = () => {
        navigate('/signup');
    };

    return (
        <div className="auth-body">
            <div className="bg-pattern"></div>

            <div className="auth-card">
                <div className="logo" style={{ justifyContent: 'center', marginBottom: '20px' }}>
                    <i className="fa-solid fa-leaf text-[1.8rem] text-persian-gold"></i>
                    <div className="logo-text">
                        <h1>ایران‌نما</h1>
                    </div>
                </div>

                <h2>ورود به حساب کاربری</h2>

                <LoginForm
                    onSuccess={handleSuccess}
                    onSwitchToSignup={handleSwitchToSignup}
                />

                <a href="/" className="back-home text-black">
                    <i className="fa-solid fa-arrow-right"></i> بازگشت به صفحه اصلی
                </a>
            </div>
        </div>
    );
};

export default Login;
