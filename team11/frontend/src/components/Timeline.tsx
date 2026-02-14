import React, { useMemo, useRef, useEffect, useState } from 'react';
import { toJalaali } from 'jalaali-js';
import MultiRangeSlider, { RangeSection } from '@/components/ui/MultiRangeSlider';
import TripItemCard from '@/components/TripItemCard';
import { TripItemWithDay } from '@/types/trip';

interface TimelineProps {
    title: string;
    items: TripItemWithDay[];
    totalDays: number;
    onItemTimeChange: (itemId: number, startTime: string, endTime: string) => void;
    onDeleteItem: (itemId: number) => void;
    onSuggestAlternative: (itemId: number) => void;
    color: string;
}

// Constants for timeline visualization
const MINUTES_PER_PIXEL = 0.3; // 0.5 minute per pixel (larger timeline)
const CARD_MAX_WIDTH = 500;
// (timeline spans `totalDays` so start/end constants not needed)

const color1 = 'bg-[#00695C]'
const color2 = 'bg-[#15a5b5]'

const Timeline: React.FC<TimelineProps> = ({
    title,
    items,
    totalDays,
    onItemTimeChange,
    onDeleteItem,
    onSuggestAlternative,
    color,
}) => {
    // Refs
    const trackContainerRef = useRef<HTMLDivElement | null>(null);
    const innerTrackRef = useRef<HTMLDivElement | null>(null);
    const cardRefs = useRef<(HTMLDivElement | null)[]>([]);
    const rafRef = useRef<number | null>(null);
    const originalItemsRef = useRef<TripItemWithDay[]>([]);

    // State
    const [hoveredIndex, setHoveredIndex] = useState<number | null>(null);
    const [visibleDay, setVisibleDay] = useState<number>(1);
    const [editingItemId, setEditingItemId] = useState<number | null>(null);
    const [pendingChanges, setPendingChanges] = useState<{ [key: number]: { startTime: string; endTime: string } }>({});
    const [activeDragSectionIndex, setActiveDragSectionIndex] = useState<number | null>(null);

    // Helper functions
    const timeToMinutesFromTripStart = (time: string, dayNumber: number): number => {
        const [hours, minutes] = time.split(':').map(Number);
        const minutesInDay = hours * 60 + minutes;
        const dayOffset = (dayNumber - 1) * 24 * 60;
        return dayOffset + minutesInDay;
    };

    const minutesToTime = (minutes: number, dayNumber: number, allowExtended: boolean = false): string => {
        const dayOffset = (dayNumber - 1) * 24 * 60;
        const minutesFromDayStart = minutes - dayOffset;

        if (allowExtended) {
            // Allow times >= 24:00 for items that extend into next day
            const hours = Math.floor(minutesFromDayStart / 60);
            const mins = minutesFromDayStart % 60;
            return `${hours.toString().padStart(2, '0')}:${mins.toString().padStart(2, '0')}`;
        } else {
            const minutesInDay = minutesFromDayStart % (24 * 60);
            const hours = Math.floor(minutesInDay / 60);
            const mins = minutesInDay % 60;
            return `${hours.toString().padStart(2, '0')}:${mins.toString().padStart(2, '0')}`;
        }
    };

    // Constants
    const totalMinutes = totalDays * 24 * 60;
    const timelineWidth = totalMinutes / MINUTES_PER_PIXEL;

    // Convert items to range sections (using pending changes if available)
    const rangeSections: RangeSection[] = useMemo(() => {
        return items.map((item) => {
            const numericId = typeof item.id === 'number' ? item.id : parseInt(String(item.id).replace(/\D/g, ''), 10);
            const pending = pendingChanges[numericId];
            const startTime = pending?.startTime || item.start_time;
            const endTime = pending?.endTime || item.end_time;

            return {
                start: timeToMinutesFromTripStart(startTime, item.day_number),
                end: timeToMinutesFromTripStart(endTime, item.day_number),
            };
        });
    }, [items, totalDays, pendingChanges]);

    // Handle range changes (client-side only, don't submit to API)
    const handleRangeChange = (sections: RangeSection[]) => {
        if (sections.length !== items.length) {
            return; // Silently skip if lengths don't match (can happen during rapid updates)
        }

        // First pass: detect which item is actually being changed in this event
        let currentlyChangingItemId: number | null = null;
        sections.forEach((section, index) => {
            const item = items[index];
            if (!item) return;

            const numericId = typeof item.id === 'number' ? item.id : parseInt(String(item.id).replace(/\D/g, ''), 10);
            if (isNaN(numericId)) return;

            const currentStartTime = pendingChanges[numericId]?.startTime || item.start_time;
            const currentEndTime = pendingChanges[numericId]?.endTime || item.end_time;
            const currentStart = timeToMinutesFromTripStart(currentStartTime, item.day_number);
            const currentEnd = timeToMinutesFromTripStart(currentEndTime, item.day_number);

            if (section.start !== currentStart || section.end !== currentEnd) {
                currentlyChangingItemId = numericId;
            }
        });

        sections.forEach((section, index) => {
            const item = items[index];
            if (!item) {
                return; // Silently skip if item not found (can happen during rapid updates)
            }

            const numericId = typeof item.id === 'number' ? item.id : parseInt(String(item.id).replace(/\D/g, ''), 10);
            if (isNaN(numericId)) return;

            // Allow if: this is the item being changed right now OR this item has pending changes
            const hasPendingChanges = pendingChanges[numericId] !== undefined;
            if (currentlyChangingItemId !== null && currentlyChangingItemId !== numericId && !hasPendingChanges) {
                return;
            }

            const newStart = section.start;
            const newEnd = section.end;

            // Enforce minimum duration of 60 minutes (1 hour)
            const duration = newEnd - newStart;
            if (duration < 60) {
                return;
            }

            // Calculate which days these fall into
            const startDay = Math.floor(newStart / (24 * 60)) + 1;
            const endDay = Math.floor((newEnd - 1) / (24 * 60)) + 1;

            // Allow items to extend into the next calendar day (but not beyond)
            // Start must be in the item's day, end can be in the same day or next day
            if (startDay !== item.day_number || endDay > item.day_number + 1) {
                return;
            }

            const dayOffset = (item.day_number - 1) * 24 * 60;
            const startMinutesFromDayStart = newStart - dayOffset;
            const endMinutesFromDayStart = newEnd - dayOffset;

            const newStartTime = minutesToTime(newStart, item.day_number, false);
            // If end extends beyond 24 hours from day start, preserve the extended format
            const newEndTime = minutesToTime(newEnd, item.day_number, endMinutesFromDayStart >= 24 * 60);

            const currentStartTime = pendingChanges[numericId]?.startTime || item.start_time;
            const currentEndTime = pendingChanges[numericId]?.endTime || item.end_time;

            if (newStartTime !== currentStartTime || newEndTime !== currentEndTime) {
                // Update pending changes and mark as editing
                setPendingChanges(prev => ({
                    ...prev,
                    [numericId]: { startTime: newStartTime, endTime: newEndTime }
                }));
                setEditingItemId(numericId);
            }
        });
    };

    // Confirm pending changes
    const handleConfirmChange = () => {
        if (editingItemId === null) return;

        const pending = pendingChanges[editingItemId];
        if (pending) {
            console.log(pending.startTime, pending.endTime)
            onItemTimeChange(editingItemId, pending.startTime, pending.endTime);
        }

        // Clear pending state
        setPendingChanges(prev => {
            const newPending = { ...prev };
            delete newPending[editingItemId];
            return newPending;
        });
        setEditingItemId(null);
        setActiveDragSectionIndex(null);
    };

    // Cancel pending changes
    const handleCancelChange = () => {
        if (editingItemId === null) return;

        // Clear pending changes for this item
        setPendingChanges(prev => {
            const newPending = { ...prev };
            delete newPending[editingItemId];
            return newPending;
        });
        setEditingItemId(null);
        setActiveDragSectionIndex(null);
    };

    // Memoized values
    const cardPositions = useMemo(() => {
        return items.map((item) => {
            const numericId = typeof item.id === 'number' ? item.id : parseInt(String(item.id).replace(/\D/g, ''), 10);
            const pending = pendingChanges[numericId];
            const startTime = pending?.startTime || item.start_time;
            const endTime = pending?.endTime || item.end_time;

            const startMinutes = timeToMinutesFromTripStart(startTime, item.day_number);
            const endMinutes = timeToMinutesFromTripStart(endTime, item.day_number);
            const durationMinutes = endMinutes - startMinutes;
            const width = Math.min(durationMinutes / MINUTES_PER_PIXEL, CARD_MAX_WIDTH);
            const translateX = (totalMinutes - startMinutes) / MINUTES_PER_PIXEL - width;

            return { width, translateX };
        });
    }, [items, totalDays, pendingChanges, totalMinutes]);

    // Event handlers
    const scrollToCard = (index: number) => {
        if (index < 0 || index >= items.length) return;
        const cardElement = cardRefs.current[index];
        if (cardElement) {
            // Save current window scroll position
            const windowScrollY = window.scrollY;
            cardElement.scrollIntoView({ behavior: 'smooth', inline: 'center' });
            // Immediately restore vertical scroll
            window.scrollTo({ top: windowScrollY, behavior: 'instant' });
        }
    };

    // Effects
    useEffect(() => {
        originalItemsRef.current = [...items];
    }, [items]);

    useEffect(() => {
        if (items.length > 0) {
            // Small delay to ensure layout is ready
            setTimeout(() => {
                const cardElement = cardRefs.current[0];
                if (cardElement) {
                    const windowScrollY = window.scrollY;
                    cardElement.scrollIntoView({ behavior: 'auto', inline: 'center' });
                    window.scrollTo({ top: windowScrollY, behavior: 'instant' });
                }
            }, 100);
        }
    }, [items.length]);

    // Update visible day based on scroll position (center of container)
    useEffect(() => {
        const container = trackContainerRef.current;
        const inner = innerTrackRef.current;
        if (!container || !inner) return;

        const update = () => {
            const containerRect = container.getBoundingClientRect();
            const innerRect = inner.getBoundingClientRect();
            const containerWidth = containerRect.width;
            // center position in viewport relative to inner track left
            const centerX = containerRect.left + containerWidth / 2 - innerRect.left;
            // RTL mapping: pixel x corresponds to time = totalMinutes - x * MINUTES_PER_PIXEL
            let minutes = Math.round(totalMinutes - centerX * MINUTES_PER_PIXEL);
            if (minutes < 0) minutes = 0;
            if (minutes > totalMinutes) minutes = totalMinutes;
            const day = Math.floor(minutes / (24 * 60)) + 1;
            setVisibleDay(day);
            rafRef.current = null;
        };

        const onScroll = () => {
            if (rafRef.current != null) return;
            rafRef.current = window.requestAnimationFrame(update) as unknown as number;
        };

        // initial set
        update();

        container.addEventListener('scroll', onScroll, { passive: true });
        return () => {
            container.removeEventListener('scroll', onScroll);
            if (rafRef.current) window.cancelAnimationFrame(rafRef.current);
        };
    }, [totalMinutes]);

    // Helper component to render visible day label with Jalali date
    interface VisibleDayLabelProps {
        visibleDay: number;
        items: TripItemWithDay[];
    }

    const persianWeekdays = [
        'یک‌شنبه',
        'دوشنبه',
        'سه‌شنبه',
        'چهارشنبه',
        'پنج‌شنبه',
        'جمعه',
        'شنبه',
    ];

    const VisibleDayLabel: React.FC<VisibleDayLabelProps> = ({ visibleDay, items }) => {
        // Try to find an item that matches the visible day
        let dateStr = items.find((i) => i.day_number === visibleDay)?.date;

        // If not found, derive from first item date + offset
        if (!dateStr && items.length > 0) {
            const first = items[0];
            const base = new Date(first.date);
            const dayOffset = visibleDay - first.day_number;
            const target = new Date(base);
            target.setDate(target.getDate() + dayOffset);
            dateStr = target.toISOString();
        }

        if (!dateStr) {
            return (
                <span className="inline-block bg-persian-blue text-white px-3 py-1 rounded shadow text-sm text-gray-700">{`روز ${visibleDay}`}</span>
            );
        }

        const gDate = new Date(dateStr);
        const weekday = persianWeekdays[gDate.getDay()];
        const { jy, jm, jd } = toJalaali(gDate.getFullYear(), gDate.getMonth() + 1, gDate.getDate());
        const jmStr = jm.toString().padStart(2, '0');
        const jdStr = jd.toString().padStart(2, '0');

        return (
            <span className={`inline-block bg-[${color}] text-white px-3 py-1 rounded shadow text-sm text-gray-700`}>{`روز ${visibleDay} - ${weekday} ${jmStr}/${jdStr}`}</span>
        );
    };

    if (items.length === 0) return null;

    return (
        <div className="mb-12">
            {/* Timeline Header */}
            <div className="mb-4 text-center pb-1 border-b-2 border-gray-200">
                <h3 className="text-xl font-bold text-gray-800">{title}</h3>
            </div>

            {/* Visible Day (updates on scroll) with inline edit buttons */}
            <div className="mb-4 text-center flex justify-center items-center gap-3">
                <VisibleDayLabel visibleDay={visibleDay} items={items} />
                {editingItemId !== null && (
                    <div className="flex gap-2">
                        <button
                            onClick={handleCancelChange}
                            className="w-7 h-7 rounded-md bg-red-500 hover:bg-red-600 text-white flex items-center justify-center shadow-md transition-all transform hover:scale-105"
                            aria-label="Cancel changes"
                        >
                            <svg width="16" height="16" viewBox="0 0 20 20" fill="none">
                                <path d="M15 5L5 15M5 5L15 15" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                            </svg>
                        </button>
                        <button
                            onClick={handleConfirmChange}
                            className="w-7 h-7 rounded-md bg-green-500 hover:bg-green-600 text-white flex items-center justify-center shadow-md transition-all transform hover:scale-105"
                            aria-label="Confirm changes"
                        >
                            <svg width="16" height="16" viewBox="0 0 20 20" fill="none">
                                <path d="M16 6L7.5 14.5L4 11" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                            </svg>
                        </button>
                    </div>
                )}
            </div>

            {/* Timeline Track */}
            <div
                className="relative"
                style={{
                    overflowX: 'auto',
                    overflowY: 'visible',
                    paddingTop: '10px',
                    paddingBottom: '10px',
                }}
                ref={trackContainerRef}
            >
                <div
                    ref={innerTrackRef}
                    style={{
                        width: `${timelineWidth}px`,
                        minWidth: '100%',
                        position: 'relative',
                    }}
                >
                    {/* Cards Container */}
                    <div className="relative mb-4" style={{ height: '240px' }}>
                        {items.map((item, index) => {
                            const { width, translateX } = cardPositions[index];
                            const showArrows = true;
                            return (
                                <div
                                    key={item.id}
                                    ref={(el) => { cardRefs.current[index] = el; }}
                                    className="absolute top-0 left-0"
                                    style={{
                                        transform: `translateX(${translateX}px)`,
                                        transition: 'transform 0.2s ease, width 0.2s ease',
                                        width: `${Math.min(width, CARD_MAX_WIDTH)}px`,
                                    }}
                                >
                                    <div
                                        onMouseEnter={() => setHoveredIndex(index)}
                                        onMouseLeave={() => setHoveredIndex((v) => (v === index ? null : v))}
                                        className="relative"
                                    >
                                        {index < items.length - 1 && (
                                            <button
                                                onClick={() => scrollToCard(index + 1)}
                                                className={`absolute -left-8 top-1/2 transform -translate-y-1/2 bg-white border hover:cursor-pointer border-gray-300 rounded-full w-7 h-7 flex items-center justify-center shadow-sm transition-opacity hover:bg-gray-50 z-10 ${showArrows ? 'opacity-100' : 'opacity-0 pointer-events-none'}`}
                                                aria-label="next"
                                            >
                                                <svg className="w-4 h-4 text-gray-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                                                </svg>
                                            </button>
                                        )}

                                        <TripItemCard
                                            item={item}
                                            width={width}
                                            maxWidth={CARD_MAX_WIDTH}
                                            onDelete={onDeleteItem}
                                            onSuggestAlternative={onSuggestAlternative}
                                        />

                                        {index > 0 && (
                                            <button
                                                onClick={() => scrollToCard(index - 1)}
                                                className={`absolute -right-8 top-1/2 transform -translate-y-1/2 bg-white  hover:cursor-pointer border-gray-300 rounded-full w-7 h-7 flex items-center justify-center shadow-sm transition-opacity hover:bg-gray-50 z-10 ${showArrows ? 'opacity-100' : 'opacity-0 pointer-events-none'}`}
                                                aria-label="prev"
                                            >
                                                <svg className="w-4 h-4 text-gray-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                                                </svg>
                                            </button>
                                        )}
                                    </div>
                                </div>
                            );
                        })}
                    </div>

                    {/* Slider with custom thumbs showing time */}
                    <MultiRangeSlider
                        sections={rangeSections}
                        min={0}
                        max={totalMinutes}
                        step={15}
                        onChange={handleRangeChange}
                        activeColor={color}
                        gapColor="#e2e8f0"
                        renderThumb={(params) => {
                            const item = items[params.sectionIndex];
                            if (!item) return null; // Safety check

                            const numericId = typeof item.id === 'number' ? item.id : parseInt(String(item.id).replace(/\D/g, ''), 10);
                            const pending = pendingChanges[numericId];
                            const startTime = pending?.startTime || item.start_time;
                            let endTime = pending?.endTime || item.end_time;

                            // Normalize endTime if it's >= 24:00
                            const [endHour, endMinute] = endTime.split(':').map(Number);
                            if (endHour >= 24) {
                                const normalizedHour = endHour % 24;
                                endTime = `${normalizedHour.toString().padStart(2, '0')}:${endMinute.toString().padStart(2, '0')}`;
                            }

                            const time = params.isStartThumb ? startTime : endTime;

                            // Track which section is being actively dragged
                            if (params.isDragged && activeDragSectionIndex !== params.sectionIndex) {
                                setActiveDragSectionIndex(params.sectionIndex);
                                setEditingItemId(numericId);
                            }

                            // Disable if any section (this one or another) is being dragged/edited and this is a different section
                            const isBeingDraggedOrEdited = activeDragSectionIndex !== null || editingItemId !== null;
                            const isThisSectionActive = activeDragSectionIndex === params.sectionIndex || editingItemId === numericId;
                            const isDisabled = isBeingDraggedOrEdited && !isThisSectionActive;

                            return (
                                <div
                                    {...params.props}
                                    key={params.props.key}
                                    style={{
                                        ...params.props.style,
                                        height: "32px",
                                        width: "32px",
                                        borderRadius: "50%",
                                        backgroundColor: isDisabled ? "#E5E7EB" : "#FFF",
                                        display: "flex",
                                        justifyContent: "center",
                                        alignItems: "center",
                                        boxShadow: isDisabled ? "0px 1px 3px #CCC" : "0px 2px 6px #AAA",
                                        cursor: isDisabled ? "not-allowed" : "grab",
                                        opacity: isDisabled ? 0.5 : 1,
                                        pointerEvents: isDisabled ? "none" : "auto",
                                    }}
                                >
                                    <svg
                                        width="20"
                                        height="16"
                                        viewBox="0 0 20 16"
                                        fill="none"
                                        style={{
                                            color: isDisabled ? "#D1D5DB" : (params.isDragged ? color : "#9CA3AF"),
                                        }}
                                    >
                                        <path d="M7 12L3 8L7 4" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                                        <path d="M13 12L17 8L13 4" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                                    </svg>
                                    <div
                                        style={{
                                            position: 'absolute',
                                            top: '100%',
                                            marginTop: '4px',
                                            fontSize: '11px',
                                            fontWeight: 600,
                                            color: '#374151',
                                            whiteSpace: 'nowrap',
                                            pointerEvents: 'none',
                                        }}
                                    >
                                        {time}
                                    </div>
                                </div>
                            );
                        }}
                    />

                    {/* Hourly markers across whole timeline */}
                    <div style={{ position: 'relative', height: 28, marginTop: 8 }}>
                        {Array.from({ length: totalMinutes / 60 + 1 }, (_, h) => h).map((hour) => {
                            const rightPercent = (hour * 60) / totalMinutes * 100;
                            const label = () => {
                                // For multi-day timeline, show day + hour when needed
                                if (hour >= 24) {
                                    const day = Math.floor(hour / 24) + 1;
                                    const hourOfDay = hour % 24;
                                    return `${hourOfDay.toString().padStart(2, '0')}:00`;
                                }
                                return `${hour.toString().padStart(2, '0')}:00`;
                            };

                            return (
                                <div key={hour} style={{ position: 'absolute', right: `${rightPercent}%`, transform: 'translateX(50%)', textAlign: 'center' }}>
                                    <div style={{ height: 6, width: 1, background: '#cbd5e1', margin: '0 auto' }} />
                                    <div className="text-xs text-gray-400 mt-1">{label()}</div>
                                </div>
                            );
                        })}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Timeline;
