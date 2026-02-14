import React, { forwardRef } from 'react';

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
}

const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ label, error, className = '', ...props }, ref) => {
    return (
      <div className="flex flex-col gap-1 text-right mb-4 w-full">
        {label && (
          <label className="text-text-dark font-bold text-sm px-1 mb-1">
            {label}
          </label>
        )}
        <input
          ref={ref}
          className={`
            w-full p-3 rounded-xl border transition-all duration-300 outline-none
            bg-white/80 font-vazir text-right
            ${error ? 'border-red-500 bg-red-50' : 'border-gray-300 focus:border-persian-gold focus:ring-2 focus:ring-persian-gold/20'}
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
  }
);

Input.displayName = 'Input';
export default Input;