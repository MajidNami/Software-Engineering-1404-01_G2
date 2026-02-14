import React, { useEffect, useState } from 'react';
import { useNotification, NotificationType } from '@/contexts/NotificationContext';

const NotificationContainer: React.FC = () => {
    const { notifications, removeNotification } = useNotification();

    return (
        <div className="fixed top-4 left-1/2 -translate-x-1/2 z-[9999] flex flex-col gap-2 min-w-[320px] max-w-md">
            {notifications.map((notification) => (
                <NotificationToast
                    key={notification.id}
                    id={notification.id}
                    type={notification.type}
                    message={notification.message}
                    onClose={() => removeNotification(notification.id)}
                />
            ))}
        </div>
    );
};

interface NotificationToastProps {
    id: string;
    type: NotificationType;
    message: string;
    onClose: () => void;
}

const NotificationToast: React.FC<NotificationToastProps> = ({
    type,
    message,
    onClose,
}) => {
    const [isExiting, setIsExiting] = useState(false);

    const handleClose = () => {
        setIsExiting(true);
        setTimeout(onClose, 300); // Match animation duration
    };

    const typeConfig = {
        success: {
            icon: 'fa-check-circle',
            bgColor: 'bg-green-50',
            borderColor: 'border-green-500',
            iconColor: 'text-green-500',
            textColor: 'text-green-800',
        },
        error: {
            icon: 'fa-times-circle',
            bgColor: 'bg-red-50',
            borderColor: 'border-red-500',
            iconColor: 'text-red-500',
            textColor: 'text-red-800',
        },
        warning: {
            icon: 'fa-exclamation-triangle',
            bgColor: 'bg-yellow-50',
            borderColor: 'border-yellow-500',
            iconColor: 'text-yellow-500',
            textColor: 'text-yellow-800',
        },
        info: {
            icon: 'fa-info-circle',
            bgColor: 'bg-blue-50',
            borderColor: 'border-blue-500',
            iconColor: 'text-blue-500',
            textColor: 'text-blue-800',
        },
    };

    const config = typeConfig[type];

    return (
        <div
            className={`${config.bgColor} ${config.borderColor} border-r-4 rounded-lg shadow-lg p-4 flex items-center gap-3 transform transition-all duration-300 ${isExiting ? 'translate-y-[-100%] opacity-0' : 'translate-y-0 opacity-100'
                }`}
        >
            <i className={`fas ${config.icon} ${config.iconColor} text-xl`}></i>
            <p className={`${config.textColor} flex-1 text-sm font-medium`}>{message}</p>
            <button
                onClick={handleClose}
                className={`${config.iconColor} hover:opacity-70 transition-opacity`}
            >
                <i className="fas fa-times"></i>
            </button>
        </div>
    );
};

export default NotificationContainer;
