import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { TripHistoryItem } from '@/types/trip';
import {
    TRAVEL_STYLES_MAP,
    BUDGET_LEVELS_MAP,
    PROGRAM_DENSITY_MAP,
    INITIAL_INTERESTS_MAP
} from '@/containers/suggest-destination/constants';
import { formatPersianCurrency } from '@/utils/costCalculations';
import Button from '@/components/ui/Button';

interface TripRowProps {
    trip: TripHistoryItem;
    onDelete: (tripId: number) => void;
    onExportPDF: (tripId: number) => void;
}

const TripRow: React.FC<TripRowProps> = ({ trip, onDelete, onExportPDF }) => {
    const navigate = useNavigate();

    const formatDate = (dateString: string) => {
        const date = new Date(dateString);
        return new Intl.DateTimeFormat('fa-IR', {
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        }).format(date);
    };

    const getStatusColor = (status: string) => {
        switch (status.toUpperCase()) {
            case 'ACTIVE':
                return 'text-leaf-green';
            case 'COMPLETED':
                return 'text-persian-blue';
            case 'CANCELLED':
                return 'text-red-500';
            default:
                return 'text-mountain-grey';
        }
    };

    const getStatusLabel = (status: string) => {
        switch (status.toUpperCase()) {
            case 'ACTIVE':
                return 'فعال';
            case 'COMPLETED':
                return 'تکمیل شده';
            case 'CANCELLED':
                return 'لغو شده';
            default:
                return status;
        }
    };

    return (
        <div
            className="group relative bg-white rounded-xl shadow-sm border border-gray-200 hover:shadow-lg transition-all duration-300 overflow-hidden"
        >
            {/* Right Border Gradient */}
            <div className="absolute right-0 top-0 bottom-0 w-1 bg-gradient-to-b from-persian-gold to-tile-cyan opacity-70 group-hover:opacity-100 group-hover:w-1.5 transition-all duration-300" />

            <div className="p-6 pr-8">
                <div className="flex items-start justify-between gap-4">
                    {/* Main Content */}
                    <div className="flex-1 min-w-0">
                        {/* Title and Status */}
                        <div className="flex items-center gap-3 mb-3">
                            <h3 className="text-xl font-black text-text-dark group-hover:text-persian-blue transition-colors">
                                {trip.title}
                            </h3>
                            <span className={`text-sm font-bold ${getStatusColor(trip.status)}`}>
                                ({getStatusLabel(trip.status)})
                            </span>
                        </div>

                        {/* Location */}
                        <div className="flex items-center gap-2 mb-3 text-mountain-grey">
                            <i className="fa-solid fa-location-dot text-persian-gold"></i>
                            <span className="font-medium">
                                {trip.province}{trip.city && trip.city !== trip.province ? ` - ${trip.city}` : ''}
                            </span>
                        </div>

                        {/* Details Grid */}
                        <div className="grid grid-cols-1 md:grid-cols-4 gap-2 mb-6 items-center">
                            {/* Dates */}
                            <div className="flex items-center gap-2 text-sm">
                                <i className="fa-solid fa-calendar text-tile-cyan"></i>
                                <div className="flex gap-3 items-center">
                                    <span className="text-xs text-mountain-grey/70">تاریخ:</span>
                                    <div className='flex flex-col'>
                                        <span className="font-medium text-text-dark">{formatDate(trip.start_date)}</span>
                                        {trip.end_date && trip.end_date !== trip.start_date && (
                                            <span className="text-xs text-mountain-grey">تا {formatDate(trip.end_date)}</span>
                                        )}
                                    </div>
                                </div>
                            </div>

                            {/* Travel Style */}
                            {trip.style && (
                                <div className="flex items-center gap-2 text-sm">
                                    <i className="fa-solid fa-users text-leaf-green"></i>
                                    <div className="flex gap-3 items-center">
                                        <span className="text-xs text-mountain-grey/70">سبک سفر:</span>
                                        <span className="font-medium text-text-dark">
                                            {TRAVEL_STYLES_MAP[trip.style.toUpperCase()] || trip.style}
                                        </span>
                                    </div>
                                </div>
                            )}

                            {/* Budget Level */}
                            <div className="flex items-center gap-2 text-sm">
                                <i className="fa-solid fa-wallet text-persian-gold"></i>
                                <div className="flex gap-3 items-center">
                                    <span className="text-xs text-mountain-grey/70">بودجه:</span>
                                    <span className="font-medium text-text-dark">
                                        {BUDGET_LEVELS_MAP[trip.budget_level.toUpperCase()] || trip.budget_level}
                                    </span>
                                </div>
                            </div>

                            {/* Interests */}
                            {trip.interests && trip.interests.length > 0 && (
                                <div className="flex items-center gap-2 text-sm flex-grow">
                                    <i className="fa-solid fa-heart text-red-400 mt-1"></i>
                                    <div className="flex gap-1 flex-grow items-center">
                                        <span className="text-xs text-mountain-grey/70">علاقه‌مندی‌ها:</span>
                                        <div className="flex flex-wrap gap-2">
                                            {trip.interests.map((interest, index) => (
                                                <span
                                                    key={index}
                                                    className="px-2 py-1 bg-bg-light text-forest-green text-xs font-medium rounded-lg border border-forest-green/20"
                                                >
                                                    {INITIAL_INTERESTS_MAP[interest.toUpperCase()] || interest}
                                                </span>
                                            ))}
                                        </div>
                                    </div>
                                </div>
                            )}
                        </div>

                        {/* Density and Total Cost */}
                        <div className="flex items-center gap-6 text-sm mb-3">
                            {trip.density && (
                                <div className="flex items-center gap-2">
                                    <i className="fa-solid fa-gauge text-persian-blue"></i>
                                    <span className="text-xs text-mountain-grey/70">تراکم برنامه:</span>
                                    <span className="font-medium text-text-dark">
                                        {PROGRAM_DENSITY_MAP[trip.density.toUpperCase()] || trip.density}
                                    </span>
                                </div>
                            )}
                            <div className="flex items-center gap-2">
                                <i className="fa-solid fa-money-bill-wave text-forest-green"></i>
                                <span className="text-xs text-mountain-grey/70">هزینه کل:</span>
                                <span className="font-bold text-forest-green">
                                    {formatPersianCurrency(trip.total_cost)}
                                </span>
                            </div>
                        </div>
                    </div>

                    {/* Action Buttons */}
                    <div className="flex flex-row gap-2 flex-shrink-0">
                        <button
                            onClick={(e) => {
                                e.stopPropagation();
                                onExportPDF(trip.id);
                            }}
                            className="flex items-center justify-center w-10 h-10 rounded-lg bg-persian-blue/10 text-persian-blue hover:bg-persian-blue hover:text-white transition-all duration-200 group/btn cursor-pointer"
                            title="دانلود PDF"
                        >
                            <i className="fa-solid fa-file-pdf text-lg"></i>
                        </button>
                        <button
                            onClick={(e) => {
                                e.stopPropagation();
                                onDelete(trip.id);
                            }}
                            className="flex items-center justify-center w-10 h-10 rounded-lg bg-red-50 text-red-500 hover:bg-red-500 hover:text-white transition-all duration-200 group/btn cursor-pointer"
                            title="حذف سفر"
                        >
                            <i className="fa-solid fa-trash text-lg"></i>
                        </button>
                    </div>
                </div>

                {/* Created Date Footer */}
                <div className="mt-4 pt-3 border-t border-gray-100 flex items-center justify-between text-xs text-mountain-grey/60">
                    <span>ایجاد شده در: {formatDate(trip.created_at)}</span>
                    <Link to={`/trip-details/${trip.id}`}>
                        <span className="text-tile-cyan hover:text-persian-gold transition-colors">
                            کلیک برای مشاهده جزئیات <i className="fa-solid fa-arrow-left mr-1"></i>
                        </span>
                    </Link>
                </div>
            </div>
        </div>
    );
};


export default TripRow;
