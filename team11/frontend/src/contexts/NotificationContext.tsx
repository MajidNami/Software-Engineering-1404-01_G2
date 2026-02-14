import React, { createContext, useContext, useState, useCallback, ReactNode } from 'react';

export type NotificationType = 'success' | 'error' | 'warning' | 'info';

export interface Notification {
    id: string;
    type: NotificationType;
    message: string;
    duration?: number;
}

interface NotificationContextType {
    notifications: Notification[];
    showNotification: (type: NotificationType, message: string, duration?: number) => void;
    removeNotification: (id: string) => void;
    success: (message: string, duration?: number) => void;
    error: (message: string, duration?: number) => void;
    warning: (message: string, duration?: number) => void;
    info: (message: string, duration?: number) => void;
}

const NotificationContext = createContext<NotificationContextType | undefined>(undefined);

export const useNotification = () => {
    const context = useContext(NotificationContext);
    if (!context) {
        throw new Error('useNotification must be used within NotificationProvider');
    }
    return context;
};

interface NotificationProviderProps {
    children: ReactNode;
}

export const NotificationProvider: React.FC<NotificationProviderProps> = ({ children }) => {
    const [notifications, setNotifications] = useState<Notification[]>([]);

    const removeNotification = useCallback((id: string) => {
        setNotifications((prev) => prev.filter((n) => n.id !== id));
    }, []);

    const showNotification = useCallback(
        (type: NotificationType, message: string, duration: number = 5000) => {
            const id = `notification-${Date.now()}-${Math.random()}`;
            const notification: Notification = { id, type, message, duration };

            setNotifications((prev) => [...prev, notification]);

            if (duration > 0) {
                setTimeout(() => {
                    removeNotification(id);
                }, duration);
            }
        },
        [removeNotification]
    );

    const success = useCallback(
        (message: string, duration?: number) => showNotification('success', message, duration),
        [showNotification]
    );

    const error = useCallback(
        (message: string, duration?: number) => showNotification('error', message, duration),
        [showNotification]
    );

    const warning = useCallback(
        (message: string, duration?: number) => showNotification('warning', message, duration),
        [showNotification]
    );

    const info = useCallback(
        (message: string, duration?: number) => showNotification('info', message, duration),
        [showNotification]
    );

    const value: NotificationContextType = {
        notifications,
        showNotification,
        removeNotification,
        success,
        error,
        warning,
        info,
    };

    return (
        <NotificationContext.Provider value={value}>{children}</NotificationContext.Provider>
    );
};
