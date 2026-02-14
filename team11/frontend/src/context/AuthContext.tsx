import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { authService, User } from '@/services/authApi';

interface AuthContextProps {
    user: User | null;
    isAuthenticated: boolean;
    isLoading: boolean;
    checkAuth: () => Promise<boolean>;
    logout: () => Promise<void>;
    setUser: (user: User | null) => void;
}

const AuthContext = createContext<AuthContextProps | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
    const [user, setUser] = useState<User | null>(null);
    const [isLoading, setIsLoading] = useState(true);

    const checkAuth = useCallback(async (): Promise<boolean> => {
        try {
            const response = await authService.verify();
            if (response.data.ok) {
                const meResponse = await authService.me();
                if (meResponse.data.ok && meResponse.data.user) {
                    setUser(meResponse.data.user);
                    return true;
                }
            }
            setUser(null);
            return false;
        } catch (error) {
            setUser(null);
            return false;
        }
    }, []);

    const logout = useCallback(async () => {
        try {
            await authService.logout();
        } catch (error) {
            console.error('Logout error:', error);
        } finally {
            setUser(null);
        }
    }, []);

    useEffect(() => {
        const initAuth = async () => {
            setIsLoading(true);
            await checkAuth();
            setIsLoading(false);
        };
        initAuth();
    }, [checkAuth]);

    return (
        <AuthContext.Provider value={{ user, isAuthenticated: !!user, isLoading, checkAuth, logout, setUser }}>
            {children}
        </AuthContext.Provider>
    );
};

export const useAuth = (): AuthContextProps => {
    const context = useContext(AuthContext);
    if (!context) {
        throw new Error('useAuth must be used within an AuthProvider');
    }
    return context;
};