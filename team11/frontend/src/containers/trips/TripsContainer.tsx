import React, { useEffect, useState } from 'react';
import { tripApi } from '@/services/api';
import { useApi } from '@/hooks/useApi';
import { TripHistoryItem } from '@/types/trip';
import TripRow from './TripRow';
import ConfirmDialog from '@/components/ui/ConfirmDialog';
import { useNotification } from '@/contexts/NotificationContext';
import { getMockTripHistory } from '@/services/mockService';

const TripsContainer: React.FC = () => {
    const { success, error: showError } = useNotification();
    const { data, isLoading, error, request } = useApi(tripApi.getHistory);
    const [trips, setTrips] = useState<TripHistoryItem[]>([]);
    const [sortBy, setSortBy] = useState<'start_date' | 'total_cost' | null>(null);
    const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('asc');
    const [confirmDialog, setConfirmDialog] = useState<{
        isOpen: boolean;
        title: string;
        message: string;
        onConfirm: () => void;
        variant?: 'danger' | 'warning' | 'info';
    }>({
        isOpen: false,
        title: '',
        message: '',
        onConfirm: () => { },
    });
    const [isDialogLoading, setIsDialogLoading] = useState(false);

    useEffect(() => {
        request();
    }, []);

    useEffect(() => {
        if (data && data.results) {
            setTrips(data.results);
        }
    }, [data]);

    const handleSort = (field: 'start_date' | 'total_cost') => {
        if (sortBy === field) {
            // Toggle order if same field
            setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
        } else {
            // Set new field with ascending order
            setSortBy(field);
            setSortOrder('asc');
        }
    };

    const getSortedTrips = () => {
        if (!sortBy) return trips;

        return [...trips].sort((a, b) => {
            let compareValue = 0;

            if (sortBy === 'start_date') {
                compareValue = new Date(a.start_date).getTime() - new Date(b.start_date).getTime();
            } else if (sortBy === 'total_cost') {
                compareValue = a.total_cost - b.total_cost;
            }

            return sortOrder === 'asc' ? compareValue : -compareValue;
        });
    };

    const handleDelete = (tripId: number) => {
        const trip = trips.find(t => t.id === tripId);

        setConfirmDialog({
            isOpen: true,
            title: 'حذف سفر',
            message: `آیا از حذف سفر "${trip?.title || 'این'}" اطمینان دارید؟ این عملیات قابل بازگشت نیست.`,
            variant: 'danger',
            onConfirm: async () => {
                setIsDialogLoading(true);
                try {
                    await tripApi.delete(tripId);
                    setTrips(prevTrips => prevTrips.filter(t => t.id !== tripId));
                    success('سفر با موفقیت حذف شد');
                } catch (err: any) {
                    console.error('Failed to delete trip:', err);
                    const errorMessage = err.response?.data?.error || 'خطا در حذف سفر. لطفاً دوباره تلاش کنید.';
                    showError(errorMessage);
                } finally {
                    setIsDialogLoading(false);
                    setConfirmDialog({ ...confirmDialog, isOpen: false });
                }
            },
        });
    };

    const handleExportPDF = async (tripId: number) => {
        try {
            const trip = trips.find(t => t.id === tripId);
            await tripApi.downloadPDF(tripId, trip?.title ? `${trip.title}.pdf` : undefined);
            success('فایل PDF با موفقیت دانلود شد');
        } catch (err: any) {
            console.error('Failed to export PDF:', err);
            const errorMessage = err.response?.data?.error || 'خطا در دانلود PDF. لطفاً دوباره تلاش کنید.';
            showError(errorMessage);
        }
    };

    // Loading State
    if (isLoading) {
        return (
            <div className="flex items-center justify-center min-h-[50vh]">
                <div className="text-center">
                    <i className="fa-solid fa-suitcase-rolling text-persian-gold text-6xl mb-4 animate-bounce"></i>
                    <p className="text-text-dark text-lg font-medium">در حال بارگذاری سفرها...</p>
                </div>
            </div>
        );
    }

    // Error State
    if (error) {
        const errorMessage = typeof error === 'object' && error !== null && 'response' in error
            ? (error as any).response?.data?.error || 'خطا در بارگذاری سفرها'
            : 'خطا در بارگذاری سفرها';

        return (
            <div className="flex items-center justify-center min-h-[50vh]">
                <div className="text-center">
                    <i className="fa-solid fa-exclamation-triangle text-red-500 text-6xl mb-4"></i>
                    <p className="text-text-dark text-lg font-medium mb-2">خطا در بارگذاری سفرها</p>
                    <p className="text-mountain-grey text-sm mb-4">
                        {errorMessage}
                    </p>
                    <button
                        onClick={() => request()}
                        className="px-6 py-2 bg-persian-blue text-white rounded-lg hover:bg-persian-blue/90 transition-colors"
                    >
                        تلاش مجدد
                    </button>
                </div>
            </div>
        );
    }

    // Empty State
    if (!trips || trips.length === 0) {
        return (
            <div className="flex items-center justify-center min-h-[50vh]">
                <div className="text-center">
                    <i className="fa-solid fa-suitcase-rolling text-persian-gold text-6xl mb-4"></i>
                    <p className="text-text-dark text-lg font-medium mb-2">هنوز سفری ایجاد نکرده‌اید</p>
                    <p className="text-mountain-grey text-sm">
                        با ایجاد اولین سفر خود، لیست سفرهایتان اینجا نمایش داده می‌شود
                    </p>
                </div>
            </div>
        );
    }

    return (
        <>
            <div className="space-y-4">
                {/* Trips Count and Sort Options */}
                <div className="flex items-center justify-center mb-6 gap-4">
                    <p className="text-mountain-grey text-sm">
                        <span className="font-bold text-persian-blue">{trips.length}</span> سفر یافت شد
                    </p>

                    {/* Sort Options */}
                    <div className="flex items-center gap-2">
                        <span className="text-sm text-mountain-grey">مرتب‌سازی:</span>
                        <button
                            onClick={() => handleSort('start_date')}
                            className={`px-3 py-1.5 text-xs font-medium rounded-lg transition-all ${sortBy === 'start_date'
                                ? 'bg-persian-blue text-white'
                                : 'bg-gray-100 text-mountain-grey hover:bg-gray-200'
                                }`}
                        >
                            تاریخ شروع
                            {sortBy === 'start_date' && (
                                <i className={`fa-solid fa-arrow-${sortOrder === 'asc' ? 'up' : 'down'} mr-1`}></i>
                            )}
                        </button>
                        <button
                            onClick={() => handleSort('total_cost')}
                            className={`px-3 py-1.5 text-xs font-medium rounded-lg transition-all ${sortBy === 'total_cost'
                                ? 'bg-persian-blue text-white'
                                : 'bg-gray-100 text-mountain-grey hover:bg-gray-200'
                                }`}
                        >
                            قیمت
                            {sortBy === 'total_cost' && (
                                <i className={`fa-solid fa-arrow-${sortOrder === 'asc' ? 'up' : 'down'} mr-1`}></i>
                            )}
                        </button>
                    </div>
                </div>

                {/* Trips List */}
                <div className="space-y-4">
                    {getSortedTrips().map((trip) => (
                        <TripRow
                            key={trip.id}
                            trip={trip}
                            onDelete={handleDelete}
                            onExportPDF={handleExportPDF}
                        />
                    ))}
                </div>
            </div>

            {/* Confirm Dialog */}
            <ConfirmDialog
                isOpen={confirmDialog.isOpen}
                title={confirmDialog.title}
                message={confirmDialog.message}
                onConfirm={confirmDialog.onConfirm}
                onClose={() => setConfirmDialog({ ...confirmDialog, isOpen: false })}
                variant={confirmDialog.variant}
                isLoading={isDialogLoading}
            />
        </>
    );
};

export default TripsContainer;
