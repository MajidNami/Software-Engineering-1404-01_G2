import { useState, useEffect, useRef } from 'react';
import { MapPin, MapPinned, Search, X } from 'lucide-react';
import placesService from '../services/placesService';

interface SearchBarProps {
  onLocationSelect: (lat: number, lng: number, name: string) => void;
  onPlaceSelect?: (facilityId: number) => void;
}

export default function SearchBar({ onLocationSelect, onPlaceSelect }: SearchBarProps) {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<{ name: string; lat: number; lng: number; fac_id: number }[]>([]);
  const [showResults, setShowResults] = useState(false);
  const [isSearching, setIsSearching] = useState(false);
  const debounceTimer = useRef<NodeJS.Timeout | null>(null);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (debounceTimer.current) {
        clearTimeout(debounceTimer.current);
      }
    };
  }, []);

  const handleSearch = (value: string) => {
    setQuery(value);
    
    // Clear previous timer
    if (debounceTimer.current) {
      clearTimeout(debounceTimer.current);
    }

    if (value.length > 0) {
      setIsSearching(true);
      
      // Debounce: wait 500ms after user stops typing
      debounceTimer.current = setTimeout(async () => {
        try {
          const searchResults = await placesService.searchByName(value);
          setResults(searchResults);
          setShowResults(true);
        } catch (error) {
          console.error('Search failed:', error);
          setResults([]);
        } finally {
          setIsSearching(false);
        }
      }, 500);
    } else {
      setResults([]);
      setShowResults(false);
      setIsSearching(false);
    }
  };

  const handleSelect = async (result: { name: string; lat: number; lng: number; fac_id: number }) => {
    setQuery(result.name);
    setShowResults(false);
    
    // If onPlaceSelect is provided, use it to open the place card
    if (onPlaceSelect) {
      onPlaceSelect(result.fac_id);
    } else {
      // Fallback to just moving the map
      onLocationSelect(result.lat, result.lng, result.name);
    }
  };

  const handleClear = () => {
    setQuery('');
    setResults([]);
    setShowResults(false);
    setIsSearching(false);
    if (debounceTimer.current) {
      clearTimeout(debounceTimer.current);
    }
  };

  return (
    <div className="relative w-full">
      <div className="flex items-center w-full px-4 gap-2 border-2 border-gray-300 rounded-xl focus-within:outline-none focus-within:ring-2 focus-within:ring-green-500 focus-within:border-transparent">
        <Search className="transform text-green-500 w-6 h-6" />
        <input
          type="text"
          value={query}
          onChange={(e) => handleSearch(e.target.value)}
          placeholder="جستجوی مکان ها..."
          className="w-full py-3 focus:outline-none"
        />
        {query && (
          <button
            onClick={handleClear}
            className="text-gray-500 hover:text-gray-700"
          >
            <X className="w-6 h-6" />
          </button>
        )}
      </div>

      {showResults && (
        <div className="absolute top-full mt-2 px-4 w-full bg-white rounded-xl shadow-lg border-2 border-gray-200 max-h-80 overflow-y-auto z-50">
          {isSearching ? (
            <div className="px-4 py-3 text-center text-gray-500">
              <div className="inline-flex items-center gap-2">
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-green-600"></div>
                در حال جستجو...
              </div>
            </div>
          ) : results.length > 0 ? (
            results.map((result) => (
              <button
                key={result.fac_id}
                onClick={() => handleSelect(result)}
                className="w-full text-left px-4 py-3 hover:bg-gray-100 border-b border-gray-300 last:border-b-0 transition-colors"
              >
                <div className="flex items-center gap-3">
                  <MapPinned className="w-6 h-6 text-gray-500" />
                  <span className="text-gray-800">{result.name}</span>
                </div>
              </button>
            ))
          ) : (
            <div className="px-4 py-3 text-center text-gray-500">
              نتیجه‌ای یافت نشد
            </div>
          )}
        </div>
      )}
    </div>
  );
}
