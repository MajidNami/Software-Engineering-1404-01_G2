import React, { useEffect, useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import Select from '../../components/ui/Select';
import Button from '../../components/ui/Button';
import ChipButton from '@/components/ui/ChipButton';
import TextField from '@/components/ui/TextField';
import { useApi } from '@/hooks/useApi';
import { destinationApi } from '@/services/api';
import {
    TRAVEL_SEASONS,
    TRAVEL_STYLES,
    GEOGRAPHIC_REGIONS,
    INITIAL_INTERESTS,
    BUDGET_LEVELS,
} from './constants';
import DestinationCard from './DestinationCard';
import { PROVINCES_DETAILS } from '@/constants';
import { useNotification } from '@/contexts/NotificationContext';

const SuggestDestinationForm = () => {
    const navigate = useNavigate();
    const resultsRef = useRef<HTMLDivElement>(null);

    const [formData, setFormData] = useState<{
        season: string | null;
        style: string | null;
        region: string | null;
    }>({
        season: null,
        style: null,
        region: null,
    });

    const [availableInterests, setAvailableInterests] = useState(INITIAL_INTERESTS);
    const [selectedInterestValues, setSelectedInterestValues] = useState<string[]>([]);
    const [isAdding, setIsAdding] = useState(false);
    const [newInterestLabel, setNewInterestLabel] = useState('');

    // useApi configured to reset data on new load for a cleaner UX
    const { isLoading, request, data: destinationsData } = useApi(destinationApi.suggest, { resetDataOnLoading: true });

    const { success: showSuccess, error: showError } = useNotification();

    // Valid if at least one selection is made or an interest is chosen
    const isFormValid = Object.values(formData).some(val => val !== null) || selectedInterestValues.length > 0;

    // Mapping API results to Province Details (Image and Persian Name)
    const destinations = destinationsData?.suggestions.map((item: { province: string }) => {
        // Find the English province key by matching Persian name
        const provinceEntry = Object.entries(PROVINCES_DETAILS).find(
            ([, detail]) => detail.name === item.province
        );
        const provinceKey = provinceEntry ? provinceEntry[0] : item.province;
        const detail = provinceEntry ? provinceEntry[1] : undefined;

        return {
            ...item,
            province: provinceKey,
            name: detail?.name || item.province,
            image: detail?.image
        };
    });

    // Auto-scroll when destinations arrive
    useEffect(() => {
        if (destinationsData && resultsRef.current) {
            resultsRef.current.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    }, [destinationsData]);

    const handleSelectChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
        const value = e.target.value === '' ? null : e.target.value;
        setFormData({ ...formData, [e.target.name]: value });
    };

    const toggleInterest = (value: string) => {
        setSelectedInterestValues(prev =>
            prev.includes(value) ? prev.filter(v => v !== value) : [...prev, value]
        );
    };

    const deleteInterest = (value: string) => {
        setAvailableInterests(prev => prev.filter(i => i.value !== value));
        setSelectedInterestValues(prev => prev.filter(v => v !== value));
    };

    const handleConfirmAdd = () => {
        if (newInterestLabel.trim()) {
            const value = newInterestLabel.toLowerCase().replace(/\s+/g, '_');
            if (!availableInterests.find(i => i.value === value)) {
                setAvailableInterests([...availableInterests, { value, label: newInterestLabel }]);
                setSelectedInterestValues([...selectedInterestValues, value]);
            }
            setNewInterestLabel('');
            setIsAdding(false);
        }
    };

    const handleSubmit = async () => {
        const payload = {
            ...formData,
            interests: selectedInterestValues,
            budget_level: BUDGET_LEVELS[1].value
        };

        try {
            await request(payload);
            showSuccess('مقاصد با موفقیت دریافت شدند!');
        } catch (error) {
            console.error('Failed to fetch destinations:', error);
            showError('خطا در دریافت مقاصد. لطفاً دوباره تلاش کنید.');
        }
    };

    return (
        <div className="w-full max-w-5xl mx-auto p-8">
            {/* Header */}
            <div className="flex items-center justify-center mb-16 relative w-full">
                <div className="section-header !mb-0 text-center">
                    <h3 className="text-3xl font-black text-text-dark">پیشنهاد مقصد</h3>
                </div>
                <div className="absolute right-0">
                    <Button variant="cancel" onClick={() => navigate('/')} className="px-5 py-2 text-xs">
                        <i className="fa-solid fa-arrow-right ml-2 text-[10px]"></i>
                        بازگشت
                    </Button>
                </div>
            </div>

            {/* Select Grid - 5 items now (added Density) */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-12">
                <Select label="فصل سفر" name="season" value={formData.season ?? ''} options={TRAVEL_SEASONS} onChange={handleSelectChange} />
                <Select label="سبک سفر" name="style" value={formData.style ?? ''} options={TRAVEL_STYLES} onChange={handleSelectChange} />
                <Select label="منطقه جغرافیایی" name="region" value={formData.region ?? ''} options={GEOGRAPHIC_REGIONS} onChange={handleSelectChange} />
            </div>

            {/* Interests Section */}
            <div className="mb-14 bg-white/40 p-6 rounded-2xl border border-white/60">
                <h4 className="font-bold mb-6 text-right text-text-dark border-r-4 border-persian-gold pr-3">انتخاب علایق</h4>
                <div className="flex flex-wrap gap-3 justify-start items-center dir-rtl">
                    {availableInterests.map((interest) => {
                        const isDeletable = !INITIAL_INTERESTS.some(initial => initial.value === interest.value);
                        return (
                            <ChipButton
                                key={interest.value}
                                label={interest.label}
                                isSelected={selectedInterestValues.includes(interest.value)}
                                onClick={() => toggleInterest(interest.value)}
                                onDelete={isDeletable ? () => deleteInterest(interest.value) : undefined}
                            />
                        );
                    })}

                    {isAdding ? (
                        <div className="flex items-center gap-2 animate-in fade-in slide-in-from-right-2">
                            <TextField
                                autoFocus
                                className="!p-2 rounded-xl border border-persian-gold bg-white text-sm outline-none w-32"
                                placeholder="عنوان..."
                                value={newInterestLabel}
                                onChange={(e) => setNewInterestLabel(e.target.value)}
                                onKeyDown={(e) => e.key === 'Enter' && handleConfirmAdd()}
                            />
                            <button onClick={handleConfirmAdd} className="text-leaf-green hover:scale-110 transition-transform">
                                <i className="fa-solid fa-circle-check text-xl"></i>
                            </button>
                            <button onClick={() => setIsAdding(false)} className="text-red-400 hover:scale-110 transition-transform">
                                <i className="fa-solid fa-circle-xmark text-xl"></i>
                            </button>
                        </div>
                    ) : (
                        <Button variant="underline" onClick={() => setIsAdding(true)} className="text-xs font-bold mr-2">
                            افزودن علاقه جدید
                            <i className="fa-solid fa-plus-circle ml-1 no-underline"></i>
                        </Button>
                    )}
                </div>
            </div>

            {/* CTA */}
            <div className="flex justify-center pt-4" ref={resultsRef} >
                <Button
                    variant="cta"
                    disabled={!isFormValid || isLoading}
                    isLoading={isLoading}
                    className="px-10 py-3 text-base rounded-xl tracking-wide disabled:grayscale disabled:opacity-50"
                    onClick={handleSubmit}
                >
                    <i className="fa-solid fa-wand-magic-sparkles ml-3"></i>
                    مشاهده مقاصد پیشنهادی
                </Button>
            </div>

            {/* Results Section with Ref for Scrolling */}
            <div className="scroll-mt-10">
                {destinations && (
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mt-20 animate-in fade-in slide-in-from-bottom-10 duration-700">
                        {destinations.map((dest: any, i: number) => (
                            <DestinationCard key={i} {...dest} style={formData.style ?? undefined} interests={selectedInterestValues} />
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
};

export default SuggestDestinationForm;