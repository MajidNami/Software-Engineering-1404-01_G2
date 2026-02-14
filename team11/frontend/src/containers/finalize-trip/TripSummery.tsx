// TripSummary.tsx
import React from 'react';
import { BUDGET_LEVELS_MAP, PROGRAM_DENSITY_MAP, TRAVEL_STYLES_MAP } from '@/containers/suggest-destination/constants';
import { formatToJalali } from '@/utils/dateUtils';


interface TripSummaryProps {
    city?: string;
    province?: string;
    start_date?: string;
    end_date?: string;
    duration_days?: number;
    style?: string;
    budget_level?: string;
    density?: string;
}

const TripSummary: React.FC<TripSummaryProps> = ({
    city,
    province,
    start_date,
    end_date,
    duration_days,
    style,
    budget_level,
    density,
}) => {
    return (
        <div className="mb-4">
            <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-4 text-sm text-gray-600">
                    {city && province && (
                        <span>
                            <i className="fa-solid fa-location-dot ml-1"></i>
                            {city}, {province}
                        </span>
                    )}
                    {start_date && end_date && (
                        <span>
                            <i className="fa-solid fa-calendar ml-1"></i>
                            {formatToJalali(start_date)} تا {formatToJalali(end_date)}
                        </span>
                    )}
                    {duration_days && (
                        <span>
                            <i className="fa-solid fa-clock ml-1"></i>
                            {duration_days} روز
                        </span>
                    )}
                </div>

                <div className="rounded-lg p-2 flex items-center justify-between">
                    <div className="flex gap-2 text-sm">
                        {style && (
                            <span className="px-3 py-1 bg-white rounded-full shadow-sm">
                                <i className="fa-solid fa-user-group ml-1 text-blue-600"></i>
                                {TRAVEL_STYLES_MAP[style]}
                            </span>
                        )}
                        {budget_level && (
                            <span className="px-3 py-1 bg-white rounded-full shadow-sm">
                                <i className="fa-solid fa-wallet ml-1 text-green-600"></i>
                                {BUDGET_LEVELS_MAP[budget_level]}
                            </span>
                        )}
                        {density && (
                            <span className="px-3 py-1 bg-white rounded-full shadow-sm">
                                <i className="fa-solid fa-chart-simple ml-1 text-red-500"></i>
                                {PROGRAM_DENSITY_MAP[density]}
                            </span>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default TripSummary;
