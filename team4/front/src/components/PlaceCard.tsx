import { useState } from 'react';
import { Star, MapPin, X, Heart, ChevronLeft, ChevronRight } from 'lucide-react';
import { Place } from '../data/mockPlaces';

interface PlaceCardProps {
  place: Place;
  onClose: () => void;
  onToggleFavorite: (place: Place) => Promise<void>;
  isFavorite: boolean;
}

export default function PlaceCard({
  place,
  onClose,
  onToggleFavorite,
  isFavorite,
}: PlaceCardProps) {
  const [currentImageIndex, setCurrentImageIndex] = useState(0);
  const [isTogglingFavorite, setIsTogglingFavorite] = useState(false);

  const nextImage = () => {
    setCurrentImageIndex((prev) => (prev + 1) % place.images.length);
  };

  const prevImage = () => {
    setCurrentImageIndex((prev) => (prev - 1 + place.images.length) % place.images.length);
  };

  const handleToggleFavorite = async () => {
    if (isTogglingFavorite) return;

    setIsTogglingFavorite(true);
    try {
      // Call parent handler which will update the state
      await onToggleFavorite(place);
    } catch (error) {
      console.error('Failed to toggle favorite:', error);
      alert('خطا در ذخیره علاقه‌مندی. لطفا دوباره تلاش کنید.');
    } finally {
      setIsTogglingFavorite(false);
    }
  };

  return (
    <div className="bg-white overflow-hidden overflow-y-auto">
      <div className="relative">
        <div className="relative h-64 bg-gray-200">
          <img
            src={place.images[currentImageIndex]}
            alt={place.name}
            className="w-full h-full object-cover"
          />

          {place.images.length > 1 && (
            <>
              <button
                onClick={prevImage}
                className="absolute left-2 top-1/2 transform -translate-y-1/2 bg-white/80 hover:bg-white p-2 rounded-full transition-colors"
              >
                <ChevronLeft className="w-5 h-5 text-gray-800" />
              </button>
              <button
                onClick={nextImage}
                className="absolute right-2 top-1/2 transform -translate-y-1/2 bg-white/80 hover:bg-white p-2 rounded-full transition-colors"
              >
                <ChevronRight className="w-5 h-5 text-gray-800" />
              </button>
            </>
          )}

          <div className="absolute bottom-2 left-1/2 transform -translate-x-1/2 flex space-x-1">
            {place.images.map((_, index) => (
              <div
                key={index}
                className={`w-2 h-2 rounded-full ${
                  index === currentImageIndex ? 'bg-white' : 'bg-white/50'
                }`}
              />
            ))}
          </div>
        </div>

        <button
          onClick={onClose}
          className="absolute top-3 right-3 bg-white/90 hover:bg-white p-2 rounded-full transition-colors shadow-md"
        >
          <X className="w-5 h-5 text-gray-800" />
        </button>

        <button
          onClick={handleToggleFavorite}
          disabled={isTogglingFavorite}
          className="absolute top-3 left-3 bg-white/90 hover:bg-white p-2 rounded-full transition-colors shadow-md disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <Heart
            className={`w-5 h-5 ${
              isFavorite ? 'fill-red-500 text-red-500' : 'text-gray-800'
            }`}
          />
        </button>
      </div>

      <div className="p-6">
        <div className="mb-4">
          <div className="flex items-start justify-between mb-2">
            <h2 className="text-2xl font-bold text-gray-800">{place.name}</h2>
            <div className="flex items-center bg-yellow-100 px-3 py-1 gap-1 rounded-full">
              <Star className="w-5 h-5 text-yellow-500 fill-current" />
              <span className="font-semibold text-gray-800">{place.rating}</span>
            </div>
          </div>

          <div className="flex items-center gap-2 text-gray-600 mb-2">
            <MapPin className="w-4 h-4" />
            <span className="text-sm">{place.address}</span>
          </div>

          <span className="inline-block px-3 py-1 bg-blue-100 text-blue-700 text-sm font-medium rounded-full uppercase">
            {place.category}
          </span>
        </div>

        <div className="mb-6">
          <h3 className="text-lg font-semibold text-gray-800 mb-2">درباره اینجا</h3>
          <p className="text-gray-600 leading-relaxed">{place.description}</p>
        </div>

        <div>
          <h3 className="text-lg font-semibold text-gray-800 mb-4">
            دیدگاه ها ({place.reviews.length})
          </h3>
          <div className="space-y-4">
            {place.reviews.map((review) => (
              <div key={review.id} className="border-b border-gray-200 pb-4 last:border-b-0">
                <div className="flex items-center justify-between mb-2">
                  <span className="font-semibold text-gray-800">{review.author}</span>
                  <div className="flex items-center">
                    {[...Array(5)].map((_, i) => (
                      <Star
                        key={i}
                        className={`w-4 h-4 ${
                          i < review.rating
                            ? 'text-yellow-500 fill-current'
                            : 'text-gray-300'
                        }`}
                      />
                    ))}
                  </div>
                </div>
                <p className="text-gray-600 text-sm mb-1">{review.comment}</p>
                <span className="text-xs text-gray-400">{review.date}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
