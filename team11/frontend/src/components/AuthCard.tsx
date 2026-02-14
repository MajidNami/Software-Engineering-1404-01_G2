import React from 'react';
import BackgroundPattern from './BackgroundPattern';

interface AuthCardProps {
  title: string;
  children: React.ReactNode;
  footerLink: { text: string; linkText: string; url: string };
}

const AuthCard: React.FC<AuthCardProps> = ({ title, children, footerLink }) => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-forest-green to-persian-blue flex items-center justify-center p-4">
      <BackgroundPattern />
      <div className="w-full max-w-md bg-white/95 backdrop-blur-xl p-10 rounded-[20px] shadow-2xl border border-white/50 text-center">
        <div className="flex justify-center items-center gap-4 mb-6">
          <i className="fa-solid fa-leaf text-3xl text-forest-green"></i>
          <h1 className="text-2xl font-black text-forest-green">ایران‌نما</h1>
        </div>

        <h2 className="text-2xl font-bold text-forest-green mb-8">{title}</h2>

        {children}

        <div className="mt-6 text-sm text-text-dark">
          {footerLink.text} <a href={footerLink.url} className="text-persian-blue font-bold hover:underline">{footerLink.linkText}</a>
        </div>

        <a href="/" className="inline-block mt-6 text-black hover:underline text-sm">
          بازگشت به صفحه اصلی <i className="fa-solid fa-arrow-left mr-2"></i>
        </a>
      </div>
    </div>
  );
};

export default AuthCard;