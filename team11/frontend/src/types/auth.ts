export interface User {
    email: string;
    first_name: string;
    last_name: string;
    age: number | null;
}

export interface SignupFormData {
    email: string;
    password: string;
    first_name: string;
    last_name: string;
    age?: number | string;
}

export interface LoginFormData {
    email: string;
    password: string;
}
