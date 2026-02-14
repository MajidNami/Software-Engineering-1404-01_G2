import React, { forwardRef } from 'react';

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'outline' | 'submit-login' | 'submit-signup' | 'info' | 'underline' | 'cta' | 'cancel';
  fullWidth?: boolean;
  isLoading?: boolean;
}

const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  ({ variant = 'primary', fullWidth, isLoading, children, className = '', ...props }, ref) => {

    const baseStyles = "font-vazir py-2 px-6 rounded-full cursor-pointer font-bold transition-all duration-300 transform active:scale-95 flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed";

    const variants = {
      primary: "bg-persian-gold text-[#3e2723] shadow-gold hover:bg-[#FFCA28] hover:-translate-y-0.5",
      secondary: "bg-[#FFE082] text-[#3e2723] shadow-md hover:bg-[#f7ba05] hover:-translate-y-0.5",
      outline: "py-2 px-4 text-xs text-forest-green bg-forest-green/10 border border-forest-green/20 rounded-lg hover:bg-forest-green hover:text-white hover:-translate-y-0.5",
      'submit-login': "bg-[#FFE082] text-[#3e2723] hover:bg-[#FFD54F] py-3 rounded-full",
      'submit-signup': "bg-persian-gold text-[#3e2723] hover:bg-[#FFCA28] py-3 rounded-full",
      info: "bg-gray-500 text-white hover:bg-gray-600 shadow-md",
      underline: "bg-transparent text-text-dark underline hover:opacity-70 !p-0 !shadow-none !translate-y-0 active:scale-100",
      cta: "bg-[#26C6DA] text-white shadow-lg hover:bg-[#00acc1] hover:-translate-y-0.5",
      cancel: "bg-[#37474F] text-white shadow-md hover:bg-[#263238] hover:-translate-y-0.5",
    };

    return (
      <button
        ref={ref}
        disabled={isLoading || props.disabled}
        className={`${baseStyles} ${variants[variant]} ${fullWidth ? "w-full" : ""} ${className}`}
        {...props}
      >
        {isLoading ? (
          <i className="fas fa-circle-notch fa-spin"></i>
        ) : children}
      </button>
    );
  }
);

Button.displayName = 'Button';
export default Button;