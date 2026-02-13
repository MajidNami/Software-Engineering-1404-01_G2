import { Heart, MapPin, Star, X } from 'lucide-react';
import { FavoritePlace } from '../services/favoritesService';

interface FavoritesPanelProps {
  favorites: FavoritePlace[];
  onClose: () => void;
  onPlaceClick: (lat: number, lng: number) => void;
  onRemoveFavorite: (facilityId: number) => void;
  onFavoriteClick: (favorite: FavoritePlace) => void;
}


export default function FavoritesPanel({
  favorites,
  onClose,
  onPlaceClick,
  onRemoveFavorite,
  onFavoriteClick,
}: FavoritesPanelProps) {
  return (
    <div className="bg-white rounded-lg shadow-lg p-6 max-h-[80vh] overflow-y-auto">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-2">
          <Heart className="w-7 h-7 text-red-500 fill-current" />
          <h2 className="text-xl font-semibold text-gray-800">علاقه مندی های من</h2>
        </div>
        <button
          onClick={onClose}
          className="text-gray-400 hover:text-gray-600 transition-colors"
        >
          <X className="w-6 h-6" />
        </button>
      </div>

      {favorites.length === 0 ? (
        <div className="text-center py-12">
          <Heart className="w-16 h-16 text-gray-300 mx-auto mb-4" />
          <p className="text-gray-500">هنوز علاقه مندی ندارید</p>
          <p className="text-sm text-gray-400 mt-2">
            مکان ها را به علاقه مندی های خود اضافه کنید تا آنها را اینجا مشاهده کنید
          </p>
        </div>
      ) : (
        <div className="space-y-4">
          {favorites.map((favorite) => {
            const detail = favorite.facility_detail;
            return (
            <div
              key={favorite.favorite_id}
              className="border-2 border-gray-200 rounded-xl p-4 hover:shadow-md transition-shadow"
            >
              <div className="flex">
                {detail.primary_image && (
                  <img
                    src={detail.primary_image}
                    alt={detail.name_fa}
                    className="w-24 h-24 object-cover rounded-lg mr-4 flex-shrink-0"
                  />
                )}
                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between mb-2">
                    <h3 className="font-semibold text-gray-800 truncate">
                      {detail.name_fa}
                    </h3>
                    <button
                      onClick={() => onRemoveFavorite(favorite.facility)}
                      className="flex-shrink-0 ml-2 text-red-500 hover:text-red-700 transition-colors"
                    >
                      <Heart className="w-5 h-5 fill-current" />
                    </button>
                  </div>

                  <div className="flex items-center gap-1 text-sm text-gray-600 mb-2">
                    <MapPin className="w-4 h-4 flex-shrink-0" />
                    <span className="truncate">{detail.city}, {detail.province}</span>
                  </div>

                  <div className="flex items-center justify-between">
                    <span className="inline-block px-2 py-1 bg-blue-100 text-blue-700 text-xs font-medium rounded capitalize">
                      {detail.category}
                    </span>
                    <div className="flex items-center gap-1">
                      <Star className="w-4 h-4 text-yellow-500 fill-current" />
                      <span className="text-sm font-medium text-gray-800">
                        {detail.avg_rating}
                      </span>
                    </div>
                  </div>

                  <button
                    onClick={() => onFavoriteClick(favorite)}
                    className="mt-3 w-full bg-blue-600 text-white py-2 rounded-lg text-sm font-medium hover:bg-blue-700 transition-colors"
                  >
                    مشاهده جزئیات
                  </button>
                </div>
              </div>
            </div>
          );})}
        </div>
      )}
    </div>
  );
}
