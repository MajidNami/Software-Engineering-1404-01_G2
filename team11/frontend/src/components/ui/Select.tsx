import React, { forwardRef } from 'react';

interface Option {
  value: string;
  label: string;
}

interface SelectProps extends React.SelectHTMLAttributes<HTMLSelectElement> {
  label?: string;
  error?: string;
  options: Option[];
}

const Select = forwardRef<HTMLSelectElement, SelectProps>(
  ({ label, error, options, className = '', ...props }, ref) => {
    return (
      <div className="flex flex-col gap-1 text-right mb-4 w-full">
        {label && (
          <label className="text-text-dark font-bold text-sm px-1 mb-1">
            {label}
          </label>
        )}
        <select
          ref={ref}
          className={`
            w-full p-3 rounded-xl border transition-all duration-300 outline-none
            bg-white/80 font-vazir text-right cursor-pointer appearance-none
            ${error ? 'border-red-500 bg-red-50' : 'border-gray-300 focus:border-persian-gold focus:ring-2 focus:ring-persian-gold/20'}
            ${className}
          `}
          {...props}
        >
          <option value="">انتخاب کنید</option>
          {options.map((opt) => (
            <option key={opt.value} value={opt.value}>
              {opt.label}
            </option>
          ))}
        </select>
        {error && (
          <span className="text-red-600 text-xs mt-1 font-medium pr-1">
            {error}
          </span>
        )}
      </div>
    );
  }
);

Select.displayName = 'Select';
export default Select;