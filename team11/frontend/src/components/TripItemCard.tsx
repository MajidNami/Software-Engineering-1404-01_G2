import React, { useState } from 'react';
import { TripItem } from '@/types/trip';

interface TripItemCardProps {
    item: TripItem;
    width: number;
    maxWidth?: number;
    onDelete: (itemId: number) => void;
    onSuggestAlternative: (itemId: number) => void;
}

const TripItemCard: React.FC<TripItemCardProps> = ({
    item,
    width,
    maxWidth = 400,
    onDelete,
    onSuggestAlternative,
}) => {
    const [isHovered, setIsHovered] = useState(false);

    const cardWidth = Math.min(width, maxWidth);

    return (
        <div
            className="relative"
            style={{ width: `${cardWidth}px`, transition: 'width 0.2s ease' }}
            onMouseEnter={() => setIsHovered(true)}
            onMouseLeave={() => setIsHovered(false)}
        >
            {/* Actions Bar - Hidden by default, shown on hover. Gradient from black to gray on hover */}
            <div
                className={`absolute top-0 py-1 left-0 right-0 rounded-t-lg transition-all duration-200 z-10 ${isHovered ? 'opacity-100 translate-y-0 bg-forest-green text-white' : 'opacity-0 -translate-y-2 pointer-events-none'
                    }`}
            >
                <div className="w-full px-3 py-2 flex items-center justify-between">
                    <button
                        onClick={() => onDelete(item.id)}
                        className="text-red-400 hover:text-red-700 hover:cursor-pointer transition-colors text-sm flex items-center"
                        title="حذف"
                    >
                        <i className="fa-solid fa-trash ml-1"></i>
                        حذف
                    </button>

                    <button
                        onClick={() => onSuggestAlternative(item.id)}
                        className="text-white hover:text-persian-gold hover:cursor-pointer transition-colors text-sm flex items-center"
                        title="پیشنهاد آیتم جایگزین"
                    >
                        <i className="fa-solid fa-wand-magic-sparkles ml-1"></i>
                        پیشنهاد جایگزین
                    </button>
                </div>
            </div>

            {/* Card Content */}
            <div className="bg-white rounded-lg shadow-xl border border-gray-200 overflow-hidden h-[260px] relative">
                {/* Gradient Side Accent - Right */}
                <div className="absolute right-0 top-0 bottom-0 w-1 bg-gradient-to-b from-forest-green to-tile-cyan opacity-80 transition-opacity" />
                {/* Gradient Side Accent - Top */}
                <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-white to-forest-green opacity-80 transition-opacity" />

                <div className="p-4 h-full flex flex-col">
                    {/* Type Badge */}
                    <div className="flex items-center justify-between mb-2">
                        <span
                            className={`text-xs font-semibold px-2 py-1 rounded ${item.type === 'VISIT'
                                ? 'bg-blue-100 text-blue-700'
                                : 'bg-purple-100 text-purple-700'
                                }`}
                        >
                            {item.category}
                        </span>
                        <span className="text-sm font-bold text-gray-700">
                            {item.cost.toLocaleString('fa-IR')} تومان
                        </span>
                    </div>

                    {/* Title */}
                    <h3 className="text-base font-bold text-gray-900 mb-2 line-clamp-1">
                        {item.title}
                    </h3>

                    {/* Summary (top ~2/3) */}
                    <p className="text-sm text-gray-600 mb-2 line-clamp-2 flex-grow">
                        {item.summery}
                    </p>

                    {/* Address & URL (bottom ~1/3) */}
                    <div className="pt-3 flex-col border-t border-gray-200 mt-2 h-[86px] text-xs text-gray-500 flex">
                        <div className="flex-1 self-start">
                            <span className="line-clamp-2 text-persian-blue">
                                <i className="fa-solid fa-location-dot ml-1"></i>
                                {item.address}
                            </span>
                        </div>

                        {item.url && (
                            <div className="self-end mr-2">
                                <a
                                    href={item.url}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className="text-blue-600 hover:text-blue-800 whitespace-nowrap"
                                    onClick={(e) => e.stopPropagation()}
                                >
                                    اطلاعات بیشتر
                                    <i className="fa-solid fa-arrow-up-right-from-square mr-1"></i>
                                </a>
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default TripItemCard;
