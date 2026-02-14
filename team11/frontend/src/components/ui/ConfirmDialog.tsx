import React, { useEffect, useRef } from 'react';
import Button from './Button';
import {
    Dialog,
    DialogContent,
    DialogHeader,
    DialogTitle,
    DialogDescription,
    DialogFooter,
    DialogOverlay,
} from './dialog';

interface ConfirmDialogProps {
    isOpen: boolean;
    onClose: () => void;
    onConfirm: () => void;
    title: string;
    message: string;
    confirmText?: string;
    cancelText?: string;
    variant?: 'danger' | 'warning' | 'info';
    isLoading?: boolean;
}

const ConfirmDialog: React.FC<ConfirmDialogProps> = ({
    isOpen,
    onClose,
    onConfirm,
    title,
    message,
    confirmText = 'تایید',
    cancelText = 'انصراف',
    variant = 'warning',
    isLoading = false,
}) => {
    const dialogRef = useRef<HTMLDivElement | null>(null);

    useEffect(() => {
        // Lock body scroll and compensate for scrollbar to avoid layout shift
        if (!isOpen) return;

        const body = document.body;
        const prevOverflow = body.style.overflow;
        const prevPaddingRight = body.style.paddingRight;
        const scrollbarWidth = window.innerWidth - document.documentElement.clientWidth;

        body.style.overflow = 'hidden';
        if (scrollbarWidth > 0) body.style.paddingRight = `${scrollbarWidth}px`;

        return () => {
            body.style.overflow = prevOverflow;
            body.style.paddingRight = prevPaddingRight;
        };
    }, [isOpen]);

    if (!isOpen) return null;

    const variantStyles = {
        danger: {
            icon: 'fa-exclamation-triangle',
            iconColor: 'text-red-500',
            iconBg: 'bg-red-100',
        },
        warning: {
            icon: 'fa-exclamation-circle',
            iconColor: 'text-yellow-500',
            iconBg: 'bg-yellow-100',
        },
        info: {
            icon: 'fa-info-circle',
            iconColor: 'text-blue-500',
            iconBg: 'bg-blue-100',
        },
    };

    const currentVariant = variantStyles[variant];

    return (
        <Dialog open={isOpen} onOpenChange={(open) => { if (!open && !isLoading) onClose(); }}>
            <DialogOverlay />
            <DialogContent className="max-w-md bg-white w-full mx-4 max-h-[80vh] overflow-y-auto">
                <DialogHeader>
                    <div className="flex items-start flex-row-reverse text-start p-4">
                        <div className={`flex-shrink-0 ${currentVariant.iconBg} rounded-full pt-1 px-1.5 ms-4`}>
                            <i className={`fas ${currentVariant.icon} ${currentVariant.iconColor} text-xl`}></i>
                        </div>
                        <div className="flex-1">
                            <DialogTitle>{title}</DialogTitle>
                            <DialogDescription className='my-2'>{message}</DialogDescription>
                        </div>
                    </div>
                </DialogHeader>

                <DialogFooter>
                    <Button
                        variant="cancel"
                        onClick={() => { if (!isLoading) onClose(); }}
                        disabled={isLoading}
                        className="px-6 py-2 text-sm"
                    >
                        {cancelText}
                    </Button>
                    <Button
                        variant="primary"
                        onClick={onConfirm}
                        isLoading={isLoading}
                        className="px-6 py-2 text-sm"
                    >
                        {confirmText}
                    </Button>
                </DialogFooter>
            </DialogContent>
        </Dialog>
    );
};

export default ConfirmDialog;
