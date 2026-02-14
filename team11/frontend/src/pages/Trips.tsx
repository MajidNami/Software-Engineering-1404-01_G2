import React from 'react';
import { useNavigate } from 'react-router-dom';
import Button from '@/components/ui/Button';
import TripsContainer from '@/containers/trips/TripsContainer';

const Trips: React.FC = () => {
    const navigate = useNavigate();

    return (
        <div className="container mx-auto py-8 px-4">
            <div className="flex items-center justify-center mb-6 relative w-full">
                <div className="section-header !mb-0 text-center">
                    <h3 className="text-3xl font-black text-text-dark">سفرهای من</h3>
                </div>
                <div className="absolute right-0">
                    <Button variant="cancel" onClick={() => navigate('/')} className="px-5 py-2 text-xs">
                        <i className="fa-solid fa-arrow-right ml-2 text-[10px]"></i>
                        بازگشت
                    </Button>
                </div>
            </div>

            <TripsContainer />
        </div>
    );
};

export default Trips;
