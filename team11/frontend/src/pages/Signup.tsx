import React from 'react';
import { useNavigate } from 'react-router-dom';
import SignupForm from '@/components/auth/SignupForm';
import { useNotification } from '@/contexts/NotificationContext';

const Signup: React.FC = () => {
    const navigate = useNavigate();
    const { success } = useNotification();

    const handleSuccess = (user: any) => {
        success(`حساب کاربری شما با موفقیت ایجاد شد. خوش آمدید ${user.first_name || user.email}`);
        navigate('/');
    };

    const handleSwitchToLogin = () => {
        navigate('/login');
    };

    return (
        <div className="auth-body">
            <div className="bg-pattern"></div>

            <div className="auth-card my-10">
                <div className="logo" style={{ justifyContent: 'center', marginBottom: '20px' }}>
                    <i className="fa-solid fa-leaf text-[1.8rem] text-persian-gold"></i>
                    <div className="logo-text">
                        <h1>ایران‌نما</h1>
                    </div>
                </div>

                <h2>ایجاد حساب جدید</h2>

                <SignupForm
                    onSuccess={handleSuccess}
                    onSwitchToLogin={handleSwitchToLogin}
                />

                <a href="/" className="back-home text-black">
                    <i className="fa-solid fa-arrow-right"></i> بازگشت به صفحه اصلی
                </a>
            </div>
        </div>
    );
};

export default Signup;
