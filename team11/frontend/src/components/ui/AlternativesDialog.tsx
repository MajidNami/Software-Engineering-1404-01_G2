import React, { useState } from 'react';
import { AlternativePlace } from '@/types/trip';
import { formatPersianCurrency } from '@/utils/costCalculations';

interface AlternativesDialogProps {
    isOpen: boolean;
    onClose: () => void;
    alternatives: AlternativePlace[];
    currentPlaceTitle: string;
    onSelectAlternative: (placeId: string) => void;
    isLoading?: boolean;
}

const AlternativesDialog: React.FC<AlternativesDialogProps> = ({
    isOpen,
    onClose,
    alternatives,
    currentPlaceTitle,
    onSelectAlternative,
    isLoading = false
}) => {
    const [selectedId, setSelectedId] = useState<string | null>(null);

    if (!isOpen) return null;

    const handleSelect = (placeId: string) => {
        setSelectedId(placeId);
        onSelectAlternative(placeId);
    };

    return (
        <div className="fixed inset-0 bg-black bg-opacity-10 flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-hidden flex flex-col">
                {/* Header */}
                <div className="px-6 py-4 border-b border-gray-200">
                    <div className="flex justify-between items-center">
                        <div>
                            <h2 className="text-xl font-bold text-gray-900">پیشنهاد جایگزین</h2>
                            <p className="text-sm text-gray-600 mt-1">
                                جایگزین برای: <span className="font-semibold">{currentPlaceTitle}</span>
                            </p>
                        </div>
                        <button
                            onClick={onClose}
                            className="text-gray-400 hover:text-gray-600 transition-colors"
                            disabled={isLoading}
                        >
                            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                            </svg>
                        </button>
                    </div>
                </div>

                {/* Content */}
                <div className="flex-1 overflow-y-auto px-6 py-4">
                    {isLoading && alternatives.length === 0 ? (
                        <div className="text-center py-12">
                            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
                            <p className="text-gray-600 font-medium">در حال دریافت پیشنهادات...</p>
                        </div>
                    ) : alternatives.length === 0 ? (
                        <div className="text-center py-12 text-gray-500">
                            <svg className="w-16 h-16 mx-auto mb-4 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4" />
                            </svg>
                            <p>جایگزینی یافت نشد</p>
                        </div>
                    ) : (
                        <div className="space-y-3">
                            {alternatives.map((alt) => (
                                <div
                                    key={alt.id}
                                    onClick={() => !isLoading && handleSelect(alt.id)}
                                    className={`
                                        p-4 border-2 rounded-lg cursor-pointer transition-all
                                        ${selectedId === alt.id
                                            ? 'border-blue-500 bg-blue-50'
                                            : 'border-gray-200 hover:border-blue-300 hover:bg-gray-50'
                                        }
                                        ${isLoading ? 'opacity-10 cursor-not-allowed' : ''}
                                    `}
                                >
                                    <div className="flex justify-between items-start gap-4">
                                        <div className="flex-1">
                                            <div className="flex items-start justify-between mb-2">
                                                <h3 className="text-lg font-semibold text-gray-900">{alt.title}</h3>
                                                <div className="flex items-center gap-2 flex-shrink-0">
                                                    {alt.rating && (
                                                        <div className="flex items-center gap-1 text-yellow-500">
                                                            <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                                                                <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                                                            </svg>
                                                            <span className="text-sm font-medium">{alt.rating.toFixed(1)}</span>
                                                        </div>
                                                    )}
                                                    {alt.price_tier && (
                                                        <span className={`
                                                            px-2 py-1 text-xs font-medium rounded
                                                            ${alt.price_tier === 'FREE' ? 'bg-green-100 text-green-800' :
                                                                alt.price_tier === 'BUDGET' ? 'bg-blue-100 text-blue-800' :
                                                                    alt.price_tier === 'MODERATE' ? 'bg-yellow-100 text-yellow-800' :
                                                                        'bg-purple-100 text-purple-800'}
                                                        `}>
                                                            {alt.price_tier === 'FREE' ? 'رایگان' :
                                                                alt.price_tier === 'BUDGET' ? 'اقتصادی' :
                                                                    alt.price_tier === 'MODERATE' ? 'متوسط' : 'لوکس'}
                                                        </span>
                                                    )}
                                                </div>
                                            </div>

                                            {alt.address && (
                                                <div className="flex items-start gap-2 text-sm text-gray-600 mb-2">
                                                    <svg className="w-4 h-4 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                                                    </svg>
                                                    <span className="flex-1">{alt.address}</span>
                                                </div>
                                            )}

                                            <div className="flex items-center gap-4 text-sm mb-2">
                                                {alt.distance !== undefined && (
                                                    <div className="flex items-center gap-1 text-gray-600">
                                                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
                                                        </svg>
                                                        <span>
                                                            {alt.distance < 1
                                                                ? `${(alt.distance * 1000).toFixed(0)} متر`
                                                                : `${alt.distance.toFixed(1)} کیلومتر`
                                                            }
                                                        </span>
                                                    </div>
                                                )}

                                                {alt.entry_fee !== undefined && (
                                                    <div className="flex items-center gap-1 text-gray-600">
                                                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                                                        </svg>
                                                        <span>
                                                            {alt.entry_fee === 0 ? 'رایگان' : formatPersianCurrency(alt.entry_fee)}
                                                        </span>
                                                    </div>
                                                )}
                                            </div>

                                            {alt.recommendation_reason && (
                                                <div className="flex items-start gap-2 mt-2">
                                                    <div className="bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm">
                                                        <span className="font-medium">💡 {alt.recommendation_reason}</span>
                                                    </div>
                                                </div>
                                            )}
                                        </div>

                                        {selectedId === alt.id && !isLoading && (
                                            <div className="flex-shrink-0 text-blue-500">
                                                <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 20 20">
                                                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                                                </svg>
                                            </div>
                                        )}
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}
                </div>

                {/* Footer */}
                <div className="px-6 py-4 border-t border-gray-200 bg-gray-50">
                    <div className="flex justify-end gap-3">
                        <button
                            onClick={onClose}
                            disabled={isLoading}
                            className="px-4 py-2 text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors disabled:opacity-10 disabled:cursor-not-allowed"
                        >
                            انصراف
                        </button>
                    </div>
                </div>

                {/* Loading Overlay - Only shown during replacement */}
                {isLoading && alternatives.length > 0 && (
                    <div className="absolute inset-0 bg-white bg-opacity-10 flex items-center justify-center">
                        <div className="flex flex-col items-center gap-3">
                            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
                            <p className="text-gray-600 font-medium">در حال جایگزینی...</p>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};

export default AlternativesDialog;
