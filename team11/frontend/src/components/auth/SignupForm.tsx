import React, { useState } from 'react';
import { authService } from '@/services/authApi';
import translateError, { BackendRaw } from '@/services/errorTranslations';
import { SignupFormData } from '@/types/auth';
import { useAuth } from '@/context/AuthContext';

interface SignupFormProps {
    onSuccess?: (user: any) => void;
    onSwitchToLogin?: () => void;
    showSwitchLink?: boolean;
}

const SignupForm: React.FC<SignupFormProps> = ({
    onSuccess,
    onSwitchToLogin,
    showSwitchLink = true
}) => {
    const { setUser } = useAuth();
    const [formData, setFormData] = useState<SignupFormData>({
        email: '',
        password: '',
        first_name: '',
        last_name: '',
        age: '',
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
            const payload = {
                email: formData.email,
                password: formData.password,
                first_name: formData.first_name,
                last_name: formData.last_name,
                ...(formData.age && { age: parseInt(formData.age as string) }),
            };

            const response = await authService.signup(payload);
            if (response.data.ok && response.data.user) {
                setUser(response.data.user); // Update global auth state
                onSuccess?.(response.data.user);
            }
        } catch (err: unknown) {
            const backend = (err as any)?.response?.data as BackendRaw | undefined;
            const translated = translateError(backend ?? (err as any));
            const errorMessage = translated || 'خطا در ثبت‌نام. لطفاً دوباره تلاش کنید.';
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
                <label>نام</label>
                <input
                    type="text"
                    name="first_name"
                    value={formData.first_name}
                    onChange={handleChange}
                    required
                />
            </div>

            <div className="form-group mb-2">
                <label>نام خانوادگی</label>
                <input
                    type="text"
                    name="last_name"
                    value={formData.last_name}
                    onChange={handleChange}
                    required
                />
            </div>

            <div className="form-group mb-2">
                <label>ایمیل</label>
                <input
                    type="email"
                    name="email"
                    value={formData.email}
                    onChange={handleChange}
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
                    required
                />
            </div>

            <div className="form-group mb-2">
                <label>سن</label>
                <input
                    type="number"
                    name="age"
                    value={formData.age}
                    onChange={handleChange}
                    min="1"
                    max="120"
                />
            </div>

            <button
                type="submit"
                className="auth-btn btn-submit-signup"
                disabled={isLoading}
            >
                {isLoading ? 'در حال ثبت‌نام...' : 'ثبت‌نام رایگان'}
            </button>

            {showSwitchLink && (
                <div className="auth-links">
                    <p>قبلاً ثبت‌نام کرده‌اید؟ <a href="#" onClick={(e) => { e.preventDefault(); onSwitchToLogin?.(); }}>وارد شوید</a></p>
                </div>
            )}
        </form>
    );
};

export default SignupForm;
