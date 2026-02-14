import { Link } from 'react-router';
import { DestinationSuggestion } from '@/types/trip';

interface DestinationCardProps extends DestinationSuggestion {
  style?: string | null;
  interests?: string[];
  image?: string
}

const DestinationCard: React.FC<DestinationCardProps> = ({
  province,
  city,
  reason,
  highlights,
  description,
  style,
  interests,
  image,
}) => {
  const params = new URLSearchParams();
  params.set('province', province);
  params.set('city', city);
  if (style) params.set('style', style);
  if (interests && interests.length) params.set('interests', interests.join(','));
  const destinationPath = `/create-trip?${params.toString()}`;

  return (
    <div className="group relative flex flex-col bg-[#E0E0E0] rounded-2xl shadow-sm border border-white/60 transition-all duration-300 hover:shadow-2xl overflow-hidden h-full">

      {/* 1. Image Area - Placeholder only, as image is not in API */}
      <div className="relative h-48 w-full bg-[#E0E0E0] overflow-hidden py-2">
        {image ? (
          <img
            src={image}
            alt={province}
            className="w-full bg-[#E0E0E0] h-full object-contain group-hover:scale-105 transition-transform duration-500"
          />
        ) : (
          <div className="w-full h-full flex items-center justify-center text-mountain-grey/20">
            <i className="fa-solid fa-image text-5xl"></i>
          </div>
        )}
      </div>

      {/* 2. Content Area - Gradient border moved here */}
      <div className="flex flex-col p-6 pt-0 -mt-6 relative z-20 flex-1">

        {/* Gradient Side Accent - Positioned specifically next to the text area */}
        <div className="absolute right-0 top-12 bottom-6 w-1 bg-gradient-to-b from-persian-gold to-tile-cyan opacity-80 group-hover:opacity-100 transition-opacity" />

        {/* City Title Tag (province removed) */}
        <div className="bg-[#BDBDBD] text-text-dark px-8 py-2 rounded-lg text-xl font-black w-fit mx-auto mb-4 shadow-md group-hover:bg-persian-blue group-hover:text-white transition-colors">
          {city}
        </div>

        {/* Description */}
        <p className="text-mountain-grey text-sm font-medium leading-relaxed text-justify dir-rtl mb-2 pr-2">
          {description}
        </p>
        {/* Separator */}
        <hr className="my-2 border-t border-gray-300" />
        {/* Reason */}
        <p className="text-persian-blue text-xs font-bold mb-4 pr-2">
          {reason}
        </p>
        {/* Highlights */}
        <div className="mb-4">
          <span className="font-bold text-xs text-forest-green">جاذبه‌ها:</span>
          <ul className="list-disc list-inside text-xs text-forest-green">
            {highlights.map((h, idx) => (
              <li key={idx}>{h}</li>
            ))}
          </ul>
        </div>
        {/* Categories
        <div className="mb-2">
          <span className="font-bold text-xs">دسته‌بندی‌ها:</span>
          <span className="text-xs text-mountain-grey ms-2">{highlights.join(', ')}</span>
        </div> */}
        {/* Removed Best Season, Score, Cost, Duration */}

        <div className='flex justify-end mt-auto items-center'>
          <span className='ms-auto'>
            <Link
              to={destinationPath}
              className="inline-flex items-center gap-2 text-text-dark font-bold text-sm border-b-2 border-text-dark pb-1 hover:text-tile-cyan hover:border-tile-cyan transition-all"
            >
              ایجاد برنامه سفر
              <i className="fa-solid fa-arrow-left text-xs"></i>
            </Link>
          </span>
        </div>
      </div>
    </div>
  );
};

export default DestinationCard;