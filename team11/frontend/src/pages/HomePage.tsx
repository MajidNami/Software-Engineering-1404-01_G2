import { useNavigate } from 'react-router-dom';
import Button from '../components/ui/Button';
import GalleryRow from '../components/GalleryRow';
import { SCROLLING_IMAGES } from '@/constants';

const firstHalf = SCROLLING_IMAGES.slice(0, Math.floor(SCROLLING_IMAGES.length / 2));
const secondHalf = SCROLLING_IMAGES.slice(Math.floor(SCROLLING_IMAGES.length / 2));

const HomePage = () => {
  const navigate = useNavigate();

  return (
    <div className="flex flex-col items-center w-full mt-2 mb-20">
      {/* Top Gallery - Moving Left to Right */}
      <GalleryRow images={firstHalf} direction="ltr" />

      {/* Main Content */}
      <div className="flex flex-col items-center justify-center py-4 space-y-12 z-10">
        <div className="text-center space-y-4">
          <h2 className="text-4xl font-black text-forest-green">برنامه‌ریزی هوشمند سفر</h2>
          <p className="text-gray-600 max-w-md mx-auto">
            تجربه‌ای متمایز در برنامه‌ریزی سفر؛ با تکمیل پرسشنامه‌های تخصصی، مقاصد و خدمات را بر اساس معیارهای دقیق خود شخصی‌سازی نمایید.
          </p>
        </div>

        <div className="flex flex-col md:flex-row gap-8 w-lg justify-center px-6 -mt-4">
          <Button
            variant="primary"
            className="flex-1 py-4 text-lg shadow-xl hover:scale-105"
            onClick={() => navigate('/create-trip')}
          >
            <i className="fa-solid fa-route ml-3"></i>
            ایجاد برنامه سفر
          </Button>

          <Button
            variant="secondary"
            className="flex-1 py-4 text-lg shadow-xl hover:scale-105 bg-persian-blue text-white hover:bg-forest-green"
            onClick={() => navigate('/suggest-destination')}
          >
            <i className="fa-solid fa-wand-magic-sparkles ml-3"></i>
            پیشنهاد مقاصد
          </Button>
        </div>
      </div>

      {/* Bottom Gallery - Moving Right to Left */}
      <GalleryRow images={secondHalf} direction="rtl" />
    </div>
  );
};

export default HomePage;