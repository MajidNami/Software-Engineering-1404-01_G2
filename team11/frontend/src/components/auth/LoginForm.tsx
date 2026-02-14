import React, { useState } from 'react';
import { authService } from '@/services/authApi';
import translateError, { BackendRaw } from '@/services/errorTranslations';
import { LoginFormData } from '@/types/auth';
import { useAuth } from '@/context/AuthContext';

interface LoginFormProps {
    onSuccess?: (user: any) => void;
    onSwitchToSignup?: () => void;
    showSwitchLink?: boolean;
}

const LoginForm: React.FC<LoginFormProps> = ({
    onSuccess,
    onSwitchToSignup,
    showSwitchLink = true
}) => {
    const { setUser } = useAuth();
    const [formData, setFormData] = useState<LoginFormData>({
        email: '',
        password: '',
    });
    const [error, setError] = useState('');
    const [isLoading, setIsLoading] = useState(false);

    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        setFormData({
            ...formData,
            [e.target.name]: e.target.value,
        });
        setError('');
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError('');
        setIsLoading(true);

        try {
            const response = await authService.login(formData);
            if (response.data.ok && response.data.user) {
                setUser(response.data.user); // Update global auth state
                onSuccess?.(response.data.user);
            }
        } catch (err: unknown) {
            const backend = (err as any)?.response?.data as BackendRaw | undefined;
            const translated = translateError(backend ?? (err as any));
            const errorMessage = translated || 'خطا در ورود. لطفاً دوباره تلاش کنید.';
            setError(errorMessage);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <form onSubmit={handleSubmit}>
            <div className={`form-alert ${error ? 'is-visible' : ''}`}>
                {error}
            </div>

            <div className="form-group mb-2">
                <label>ایمیل</label>
                <input
                    type="email"
                    name="email"
                    value={formData.email}
                    onChange={handleChange}
                    placeholder="مثال: ali.rezai@gmail.com"
                    required
                />
            </div>

            <div className="form-group mb-2">
                <label>رمز عبور</label>
                <input
                    type="password"
                    name="password"
                    value={formData.password}
                    onChange={handleChange}
                    placeholder="********"
                    required
                />
            </div>

            <button
                type="submit"
                className="auth-btn btn-submit-login"
                disabled={isLoading}
            >
                {isLoading ? 'در حال ورود...' : 'ورود'}
            </button>

            {showSwitchLink && (
                <div className="auth-links">
                    <p>حساب کاربری ندارید؟ <a href="#" onClick={(e) => { e.preventDefault(); onSwitchToSignup?.(); }}>ثبت‌نام کنید</a></p>
                </div>
            )}
        </form>
    );
};

export default LoginForm;
