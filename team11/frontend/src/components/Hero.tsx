import React from 'react';

const Hero: React.FC = () => {
  return (
    <section className="relative h-[380px] flex items-center justify-center text-center text-white rounded-b-[50px] overflow-hidden mb-[-50px]">
      <div className="absolute inset-0 bg-gradient-to-b from-persian-blue/90 to-forest-green/80 z-10" />
      <img 
        src="https://images.unsplash.com/photo-1590059392231-64157e3f898a?q=80&w=1600" 
        className="absolute inset-0 w-full h-full object-cover"
        alt="Iran Nature"
      />
      
      <div className="relative z-20 px-4 space-y-4">
        <h2 className="text-3xl md:text-5xl font-black drop-shadow-lg">
          کاوش در طبیعت و فرهنگ ایران
        </h2>
        <p className="text-sm md:text-lg opacity-90 font-light">
          سامانه جامع خدمات گردشگری، جغرافیا و ایران‌شناسی
        </p>
      </div>
    </section>
  );
};

export default Hero;