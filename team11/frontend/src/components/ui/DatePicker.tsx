import React from "react";
import { InputDatePicker } from "jalaali-react-date-picker";
import type { Moment } from "moment";

interface DatePickerProps {
  label?: string;
  error?: string;
  value?: Moment | null;
  onChange?: (date: Moment | null, dateString: string) => void;
  disabledDates?: (current: Moment) => boolean;
  placeholder?: string;
  disabled?: boolean;
  className?: string;
  [key: string]: any;
}

const DatePicker: React.FC<DatePickerProps> = ({
  label,
  error,
  className = '',
  ...props
}) => {
  return (
    <div className="flex flex-col gap-1 text-right w-full">
      {label && (
        <label className="text-text-dark font-bold text-sm px-1 mb-1">
          {label}
        </label>
      )}
      <InputDatePicker
        error={!!error}
        style={{ height: '3.05rem', borderRadius: '1rem' }}
        wrapperStyle={{ height: '3.05rem', borderRadius: '1rem' }}
        wrapperClassName={`
          rounded-xl border transition-all duration-300
          ${error ? 'border-red-500 bg-red-50' : 'border-gray-300 focus-within:border-persian-gold focus-within:ring-2 focus-within:ring-persian-gold/20'}
          ${className}
        `}
        {...props}
      />
      {error && (
        <span className="text-red-600 text-xs mt-1 font-medium pr-1">
          {error}
        </span>
      )}
    </div>
  );
};

export default DatePicker;