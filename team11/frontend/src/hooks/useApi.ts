import { useState } from 'react';

interface ApiConfig {
    resetDataOnLoading?: boolean;
}

export const useApi = (apiFunc: any, config: ApiConfig = { resetDataOnLoading: false }) => {
    const [data, setData] = useState<any>(null);
    const [error, setError] = useState<string | null>(null);
    const [isLoading, setLoading] = useState<boolean>(false);

    const request = async (...args: any[]) => {
        setLoading(true);
        setError(null);

        // Configurable reset logic
        if (config.resetDataOnLoading) {
            setData(null);
        }

        try {
            const response = await apiFunc(...args);
            // Accessing response.data assuming standard Axios-like structure
            const result = response.data || response;
            setData(result);
            return result;
        } catch (err: any) {
            const msg = err.response?.data?.message || "خطایی در برقراری ارتباط رخ داد";
            setError(msg);
            throw err;
        } finally {
            setLoading(false);
        }
    };

    return { data, error, isLoading, request, setData };
};