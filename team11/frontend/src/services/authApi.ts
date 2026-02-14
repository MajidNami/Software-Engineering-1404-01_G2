import axios, { AxiosResponse } from 'axios';

const authApi = axios.create({
    baseURL: import.meta.env.VITE_AUTH_BASE_URL || '/auth',
    headers: {
        'Content-Type': 'application/json',
    },
    withCredentials: true, // For JWT in cookies
});

export interface User {
    email: string;
    first_name: string;
    last_name: string;
    age: number | null;
}

export interface SignupPayload {
    email: string;
    password: string;
    first_name: string;
    last_name: string;
    age?: number;
}

export interface LoginPayload {
    email: string;
    password: string;
}

export interface AuthResponse {
    ok: boolean;
    user: User;
}

export interface VerifyResponse {
    ok: boolean;
}

export const authService = {
    // Signup
    signup: (data: SignupPayload): Promise<AxiosResponse<AuthResponse>> => 
        authApi.post('/signup/', data),

    // Login
    login: (data: LoginPayload): Promise<AxiosResponse<AuthResponse>> => 
        authApi.post('/login/', data),

    // Logout
    logout: (): Promise<AxiosResponse<{ ok: boolean }>> => 
        authApi.post('/logout/'),

    // Get Current User
    me: (): Promise<AxiosResponse<AuthResponse>> => 
        authApi.get('/me/'),

    // Verify Token
    verify: (): Promise<AxiosResponse<VerifyResponse>> => 
        authApi.get('/verify/'),

    // Refresh Token
    refresh: (): Promise<AxiosResponse<{ ok: boolean }>> => 
        authApi.post('/refresh/'),
};

export default authService;
