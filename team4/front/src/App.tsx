import { useState, useEffect } from 'react';
import {
  Navigation,
  Heart,
  Menu,
  X,
  MapPin,
} from 'lucide-react';
import MapView from './components/MapView';
import SearchBar from './components/SearchBar';
import CategoryFilter from './components/CategoryFilter';
import PlaceCard from './components/PlaceCard';
import RoutingPanel from './components/RoutingPanel';
import FavoritesPanel from './components/FavoritesPanel';
import { Place } from './data/mockPlaces';
import { Route } from './data/mockRoutes';
import placesService from './services/placesService';
// import { favoritesService, FavoritePlace } from './services/favoritesService';

const MOCK_USER_ID = 'demo-user-123';

function App() {
  const [mapCenter, setMapCenter] = useState<[number, number]>([40.7589, -73.9851]);
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
  // const [favorites, setFavorites] = useState<FavoritePlace[]>([]);
  const [favoritePlaceIds, setFavoritePlaceIds] = useState<Set<string>>(new Set());

  const cardStyle = 
    "absolute right-4 top-4 w-96 max-w-[90vw] h-[90%] z-10 overflow-auto rounded-lg";

  // Load facilities on mount
  useEffect(() => {
    loadFacilities();
  }, []);

  // Filter places when category changes
  useEffect(() => {
    if (selectedCategory === 'all') {
      setFilteredPlaces(allPlaces);
    } else {
      setFilteredPlaces(allPlaces.filter((place) => place.category === selectedCategory));
    }
  }, [selectedCategory, allPlaces]);

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

  // useEffect(() => {
  //   loadFavorites();
  // }, []);

  // const loadFavorites = async () => {
  //   try {
  //     const userFavorites = await favoritesService.getFavorites(MOCK_USER_ID);
  //     setFavorites(userFavorites);
  //     setFavoritePlaceIds(new Set(userFavorites.map((f) => f.place_id)));
  //   } catch (error) {
  //     console.error('Failed to load favorites:', error);
  //   }
  // };

  const handleCategoryChange = async (category: string) => {
    setSelectedCategory(category);
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

  const handleLocationSelect = (lat: number, lng: number) => {
    setMapCenter([lat, lng]);
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
    calculatedRoute: Route,
    source: [number, number],
    destination: [number, number]
  ) => {
    setRoute(calculatedRoute.coordinates);
    setSourceMarker(source);
    setDestinationMarker(destination);
    const midLat = (source[0] + destination[0]) / 2;
    const midLng = (source[1] + destination[1]) / 2;
    setMapCenter([midLat, midLng]);
  };

  const handleToggleFavorite = async (place: Place) => {
    // try {
    //   if (favoritePlaceIds.has(place.id)) {
    //     await favoritesService.removeFavorite(place.id, MOCK_USER_ID);
    //     setFavoritePlaceIds((prev) => {
    //       const newSet = new Set(prev);
    //       newSet.delete(place.id);
    //       return newSet;
    //     });
    //   } else {
    //     await favoritesService.addFavorite(place, MOCK_USER_ID);
    //     setFavoritePlaceIds((prev) => new Set([...prev, place.id]));
    //   }
    //   await loadFavorites();
    // } catch (error) {
    //   console.error('Failed to toggle favorite:', error);
    // }
    console.log("add to favorite", place);
  };

  const handleRemoveFavorite = async (placeId: string) => {
    // try {
    //   await favoritesService.removeFavorite(placeId, MOCK_USER_ID);
    //   setFavoritePlaceIds((prev) => {
    //     const newSet = new Set(prev);
    //     newSet.delete(placeId);
    //     return newSet;
    //   });
    //   await loadFavorites();
    // } catch (error) {
    //   console.error('Failed to remove favorite:', error);
    // }
  };

  const handleCloseRouting = () => {
    setShowRouting(false);
    setRoute(null);
    setSourceMarker(null);
    setDestinationMarker(null);
  };

  return (
    <div className="h-screen flex flex-col overflow-hidden bg-gray-50">
      <header className="bg-white shadow-md z-50">
        <div className="px-4 py-4">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center">
              <MapPin className="w-8 h-8 text-blue-600 mr-2" />
              <h1 className="text-2xl font-bold text-gray-800">ExploreMap</h1>
            </div>

            <div className="flex items-center space-x-2">
              <button
                onClick={() => setShowRouting(!showRouting)}
                className={`flex items-center px-4 py-2 rounded-lg font-medium transition-colors ${
                  showRouting
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                <Navigation className="w-5 h-5 mr-2" />
                <span className="hidden sm:inline">Routing</span>
              </button>

              <button
                onClick={() => setShowFavorites(!showFavorites)}
                className={`flex items-center px-4 py-2 rounded-lg font-medium transition-colors ${
                  showFavorites
                    ? 'bg-red-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                <Heart className="w-5 h-5 mr-2" />
                <span className="hidden sm:inline">Favorites</span>
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
                {showSidebar ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
              </button>
            </div>
          </div>

          <div>
            <SearchBar onLocationSelect={handleLocationSelect} />
          </div>
        </div>
      </header>

      <div className="flex-1 flex overflow-hidden">
        <aside
          className={`${
            showSidebar ? 'translate-x-0' : '-translate-x-full'
          } lg:translate-x-0 fixed lg:relative z-20 w-80 h-[-webkit-fill-available] bg-white shadow-lg transition-transform duration-300 overflow-y-auto`}
        >
          <div className="p-4 space-y-4">
            <CategoryFilter
              selectedCategory={selectedCategory}
              onCategoryChange={handleCategoryChange}
            />

            <div>
              <h3 className="text-lg font-semibold text-gray-800 mb-3">
                Nearby Places ({filteredPlaces.length})
              </h3>
              {isLoading ? (
                <div className="flex items-center justify-center py-8">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
                  <span className="ml-3 text-gray-600">Loading places...</span>
                </div>
              ) : filteredPlaces.length === 0 ? (
                <div className="text-center py-8 text-gray-500">
                  <p>No places found</p>
                  <p className="text-sm mt-2">Try changing your filters</p>
                </div>
              ) : (
                <div className="space-y-3">
                  {filteredPlaces.map((place) => (
                    <button
                      key={place.id}
                      onClick={() => handlePlaceSelect(place)}
                      className="w-full text-left p-3 border border-gray-200 rounded-lg hover:border-blue-500 hover:shadow-md transition-all"
                    >
                      <div className="flex items-start">
                        <img
                          src={place.images[0]}
                          alt={place.name}
                          className="w-16 h-16 object-cover rounded-lg mr-3"
                        />
                        <div className="flex-1 min-w-0">
                          <h4 className="font-semibold text-gray-800 truncate">
                            {place.name}
                          </h4>
                          <p className="text-sm text-gray-600 capitalize">
                            {place.category}
                          </p>
                          <div className="flex items-center mt-1">
                            <span className="text-yellow-500 text-sm">★</span>
                            <span className="text-sm font-medium text-gray-800 ml-1">
                              {place.rating}
                            </span>
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
                favorites={[]}
                onClose={() => setShowFavorites(false)}
                onPlaceClick={handleLocationSelect}
                onRemoveFavorite={handleRemoveFavorite}
              />
            </div>
          )}
        </main>
      </div>
    </div>
  );
}

export default App;
