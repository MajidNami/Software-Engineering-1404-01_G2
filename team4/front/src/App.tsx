import { useState, useEffect } from 'react';
import {
  Navigation,
  Heart,
  Menu,
  X,
  MapPin,
  Star,
} from 'lucide-react';
import MapView from './components/MapView';
import SearchBar from './components/SearchBar';
import CategoryFilter from './components/CategoryFilter';
import PlaceCard from './components/PlaceCard';
import RoutingPanel from './components/RoutingPanel';
import FavoritesPanel from './components/FavoritesPanel';
import { Place } from './data/mockPlaces';
import placesService from './services/placesService';
import polyline from "@mapbox/polyline";
import { favoritesService, FavoritePlace } from './services/favoritesService';
import { RouteResponse } from './data/types';

function App() {
  const [mapCenter, setMapCenter] = useState<[number, number]>([35.729054, 51.42047]);
  const [allPlaces, setAllPlaces] = useState<Place[]>([]);
  const [filteredPlaces, setFilteredPlaces] = useState<Place[]>([]);
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [selectedPlace, setSelectedPlace] = useState<Place | null>(null);
  const [showRouting, setShowRouting] = useState(false);
  const [showFavorites, setShowFavorites] = useState(false);
  const [showSidebar, setShowSidebar] = useState(true);
  const [route, setRoute] = useState<[number, number][] | null>(null);
  const [sourceMarker, setSourceMarker] = useState<[number, number] | null>(null);
  const [destinationMarker, setDestinationMarker] = useState<[number, number] | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [favoritePlaceIds, setFavoritePlaceIds] = useState<Set<string>>(new Set());
  const [favorites, setFavorites] = useState<FavoritePlace[]>([]);

  const cardStyle = 
    "absolute end-4 top-4 w-96 max-w-[90vw] h-[90%] z-10 overflow-auto rounded-lg";

  // Load facilities on mount
  useEffect(() => {
    loadFacilities();
    loadFavoriteIds();
  }, []);

  const loadFavoriteIds = async () => {
    try {
      const favorites = await favoritesService.getFavorites();
      // Extract facility IDs from favorites and add to set
      const ids = new Set(favorites.map(fav => fav.facility.toString()));
      setFavoritePlaceIds(ids);
    } catch (error) {
      console.error('Failed to load favorites:', error);
      // Don't show error to user - favorites are optional feature
    }
  };

  // Filter places when category changes (removed - now handled in handleCategoryChange)
  // useEffect(() => {
  //   if (selectedCategory === 'all') {
  //     setFilteredPlaces(allPlaces);
  //   } else {
  //     setFilteredPlaces(allPlaces.filter((place) => place.category === selectedCategory));
  //   }
  // }, [selectedCategory, allPlaces]);

  // Load favorites when panel opens
  useEffect(() => {
    if (showFavorites) {
      loadFavorites();
    }
  }, [showFavorites]);

  const loadFacilities = async () => {
    setIsLoading(true);
    try {
      const facilities = await placesService.getFacilities({ page_size: 100 });
      setAllPlaces(facilities);
      setFilteredPlaces(facilities);
      
      // Set initial map center to first facility if available
      if (facilities.length > 0) {
        setMapCenter([facilities[0].latitude, facilities[0].longitude]);
      }
    } catch (error) {
      console.error('Failed to load facilities:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const loadFavorites = async () => {
    setIsLoading(true);
    try {
      const userFavorites = await favoritesService.getFavorites();
      setFavorites(userFavorites);
    } catch (error) {
      console.error('Failed to load favorites:', error);
      // Don't show alert - user might not be logged in
    } finally {
      setIsLoading(false);
    }
  };

  const handleCategoryChange = async (category: string) => {
    setSelectedCategory(category);
    setFilteredPlaces([]);
    setIsLoading(true);
    
    try {
      if (category === 'all') {
        const facilities = await placesService.getFacilities({ page_size: 100 });
        setAllPlaces(facilities);
        setFilteredPlaces(facilities);
      } else {
        const facilities = await placesService.getFacilitiesByCategory(category);
        setFilteredPlaces(facilities);
      }
    } catch (error) {
      console.error('Failed to filter facilities:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleLocationSelect = (lat: number, lng: number, name?: string) => {
    setMapCenter([lat, lng]);
    // Could use name for something in the future
  };

  const handleSearchPlaceSelect = async (facilityId: number) => {
    // Close other panels to show place card clearly
    setShowRouting(false);
    setShowFavorites(false);
    setShowSidebar(false); // Close sidebar on mobile
    
    // Clear route if exists
    setRoute(null);
    setSourceMarker(null);
    setDestinationMarker(null);
    
    // Fetch detailed information for the facility by ID
    setIsLoading(true);
    try {
      const detailedPlace = await placesService.getFacilityDetails(facilityId.toString());
      if (detailedPlace) {
        setSelectedPlace(detailedPlace);
        setMapCenter([detailedPlace.latitude, detailedPlace.longitude]);
      }
    } catch (error) {
      console.error('Failed to fetch place details from search:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handlePlaceSelect = async (place: Place) => {
    // Fetch detailed information for the place
    setIsLoading(true);
    try {
      const detailedPlace = await placesService.getFacilityDetails(place.id);
      setSelectedPlace(detailedPlace || place);
      setMapCenter([place.latitude, place.longitude]);
    } catch (error) {
      console.error('Failed to fetch place details:', error);
      setSelectedPlace(place);
      setMapCenter([place.latitude, place.longitude]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleRouteCalculated = (
    calculatedRoute: RouteResponse,
    source: [number, number],
    destination: [number, number]
  ) => {
    setRoute(polyline.decode(calculatedRoute.routes[0].overview_polyline.points));
    console.log(calculatedRoute);
    console.log(polyline.decode(calculatedRoute.routes[0].overview_polyline.points));
    setSourceMarker(source);
    setDestinationMarker(destination);
    const midLat = (source[0] + destination[0]) / 2;
    const midLng = (source[1] + destination[1]) / 2;
    setMapCenter([midLat, midLng]);
  };

  const handleToggleFavorite = async (place: Place) => {
    try {
      const response = await favoritesService.toggleFavorite(Number(place.id));
      
      // Update local state based on server response
      if (response.favorited) {
        setFavoritePlaceIds((prev) => new Set([...prev, place.id]));
      } else {
        setFavoritePlaceIds((prev) => {
          const newSet = new Set(prev);
          newSet.delete(place.id);
          return newSet;
        });
      }
    } catch (error) {
      console.error('Failed to toggle favorite:', error);
      throw error; // Re-throw to let PlaceCard handle the error
    }
  };

  const handleRemoveFavorite = async (facilityId: number) => {
    try {
      await favoritesService.toggleFavorite(facilityId);
      // Remove from local state
      setFavoritePlaceIds((prev) => {
        const newSet = new Set(prev);
        newSet.delete(facilityId.toString());
        return newSet;
      });
      // Reload favorites list
      await loadFavorites();
    } catch (error) {
      console.error('Failed to remove favorite:', error);
      alert('خطا در حذف علاقه‌مندی. لطفا دوباره تلاش کنید.');
    }
  };

  const handleFavoriteClick = async (favorite: FavoritePlace) => {
    // Close favorites panel
    setShowFavorites(false);
    
    // Try to fetch full place details
    setIsLoading(true);
    try {
      const placeDetails = await placesService.getFacilityDetails(favorite.facility.toString());
      if (placeDetails) {
        setSelectedPlace(placeDetails);
        setMapCenter([placeDetails.latitude, placeDetails.longitude]);
      } else {
        // If can't fetch details, create a minimal Place object from favorite
        const detail = favorite.facility_detail;
        const minimalPlace: Place = {
          id: detail.fac_id.toString(),
          name: detail.name_fa,
          category: detail.category,
          latitude: detail.location.coordinates[1],
          longitude: detail.location.coordinates[0],
          rating: parseFloat(detail.avg_rating) || 0,
          address: `${detail.city}, ${detail.province}`,
          description: detail.name_fa,
          images: detail.primary_image ? [detail.primary_image] : [],
          reviews: [],
        };
        setSelectedPlace(minimalPlace);
        setMapCenter([minimalPlace.latitude, minimalPlace.longitude]);
      }
    } catch (error) {
      console.error('Failed to load place details:', error);
      // Fallback: use data from favorite
      const detail = favorite.facility_detail;
      const minimalPlace: Place = {
        id: detail.fac_id.toString(),
        name: detail.name_fa,
        category: detail.category,
        latitude: detail.location.coordinates[1],
        longitude: detail.location.coordinates[0],
        rating: parseFloat(detail.avg_rating) || 0,
        address: `${detail.city}, ${detail.province}`,
        description: detail.name_fa,
        images: detail.primary_image ? [detail.primary_image] : [],
        reviews: [],
      };
      setSelectedPlace(minimalPlace);
      setMapCenter([minimalPlace.latitude, minimalPlace.longitude]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleCloseRouting = () => {
    setShowRouting(false);
    setRoute(null);
    setSourceMarker(null);
    setDestinationMarker(null);
  };

  const handleNearbyPlaces = (places: Place[]) => {
    setFilteredPlaces(places);
  }

  return (
    <div className="h-screen flex flex-col overflow-hidden bg-gray-50">
      <header className="bg-white shadow-md z-50">
        <div className="px-4 py-4">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <MapPin className="w-8 h-8 text-orange-600" />
              <h1 className="text-2xl font-bold text-gray-800 hidden sm:inline">نقشه امکانات رفاهی</h1>
              <h1 className="text-2xl font-bold text-gray-800 inline sm:hidden">نار</h1>
            </div>

            <div className="flex items-center gap-2">
              <button
                onClick={() => setShowRouting(!showRouting)}
                className={`flex items-center px-4 py-2 gap-2 rounded-lg font-medium transition-colors ${
                  showRouting
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                <Navigation className="w-6 h-6 fill-current" />
                <span className="hidden sm:inline">مسیریابی</span>
              </button>

              <button
                onClick={() => setShowFavorites(!showFavorites)}
                className={`flex items-center px-4 py-2 gap-2 rounded-lg font-medium transition-colors ${
                  showFavorites
                    ? 'bg-red-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                <Heart className="w-6 h-6 fill-current" />
                <span className="hidden sm:inline">علاقه مندی ها</span>
                {/* favorites.length > 0 && (
                  <span className="ml-2 bg-white text-red-600 text-xs font-bold px-2 py-1 rounded-full">
                    {favorites.length}
                  </span>
                ) */}
              </button>

              <button
                onClick={() => setShowSidebar(!showSidebar)}
                className="lg:hidden flex items-center px-3 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors"
              >
                {showSidebar ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
              </button>
            </div>
          </div>

          <div>
            <SearchBar 
              onLocationSelect={handleLocationSelect}
              onPlaceSelect={handleSearchPlaceSelect}
            />
          </div>
        </div>
      </header>

      <div className="flex-1 flex overflow-hidden">
        <aside
          className={`${
            showSidebar ? 'translate-x-0' : 'translate-x-full'
          } lg:translate-x-0 fixed lg:relative z-20 w-80 h-[-webkit-fill-available] bg-white shadow-lg transition-transform duration-300 overflow-y-auto`}
        >
          <div className="p-4 space-y-4">
            <CategoryFilter
              selectedCategory={selectedCategory}
              onCategoryChange={handleCategoryChange}
            />

            <div>
              <h3 className="text-lg font-semibold text-gray-800 mb-3">
                مکان های نزدیک ({filteredPlaces.length})
              </h3>
              {isLoading ? (
                <div className="flex items-center justify-center py-8 gap-3">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
                  <span className="text-gray-600">بارگذاری...</span>
                </div>
              ) : filteredPlaces.length === 0 ? (
                <div className="text-center py-8 text-gray-500">
                  <p>مکانی یافت نشد</p>
                  <p className="text-sm mt-2">دسته بندی را عوض کنید</p>
                </div>
              ) : (
                <div className="space-y-3">
                  {filteredPlaces.map((place) => (
                    <button
                    key={place.id}
                    onClick={() => handlePlaceSelect(place)}
                    className="w-full text-start p-3 border-2 border-gray-200 rounded-xl hover:border-orange-500 hover:shadow-md transition-all"
                  >
                    <div className="flex items-center gap-3">
                      <img
                        src={place.images[0]}
                        alt={place.name}
                        className="w-16 h-16 object-cover rounded-lg"
                      />
                      <div className="flex flex-col gap-1 min-w-0">
                        <h4 className="font-semibold text-gray-800 truncate">
                          {place.name}
                        </h4>
                        <p className="text-sm text-gray-600 uppercase">
                          {place.category}
                        </p>
                        <div className="flex items-center bg-yellow-100 px-1 w-fit gap-1 rounded-full">
                          <Star className="w-4 h-4 text-yellow-500 fill-current" />
                          <span className="font-semibold text-gray-800">{place.rating}</span>
                        </div>
                      </div>
                    </div>
                  </button>
                  ))}
                </div>
              )}
            </div>
          </div>
        </aside>

        <main className="flex-1 relative">
          <MapView
            places={filteredPlaces}
            center={mapCenter}
            selectedPlace={selectedPlace}
            onPlaceSelect={handlePlaceSelect}
            route={route}
            sourceMarker={sourceMarker}
            destinationMarker={destinationMarker}
            onFindNearbyPlaces={handleNearbyPlaces}
          />

          {selectedPlace && (
            <div className={cardStyle}>
              <PlaceCard
                place={selectedPlace}
                onClose={() => setSelectedPlace(null)}
                onToggleFavorite={handleToggleFavorite}
                isFavorite={favoritePlaceIds.has(selectedPlace.id)}
              />
            </div>
          )}

          {showRouting && (
            <div className={cardStyle}>
              <RoutingPanel
                onRouteCalculated={handleRouteCalculated}
                onClose={handleCloseRouting}
              />
            </div>
          )}

          {showFavorites && (
            <div className={cardStyle}>
              <FavoritesPanel
                favorites={favorites}
                onClose={() => setShowFavorites(false)}
                onPlaceClick={(lat, lng) => {
                  setMapCenter([lat, lng]);
                  setShowFavorites(false);
                }}
                onRemoveFavorite={handleRemoveFavorite}
                onFavoriteClick={handleFavoriteClick}
              />
            </div>
          )}

        </main>
      </div>
    </div>
  );
}

export default App;
