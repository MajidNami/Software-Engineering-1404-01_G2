import { useState } from 'react';
import { Navigation, MapPin, Clock, X, Building2, MapPinned, ArrowLeft, Route, Waypoints, WaypointsIcon, LucideWaypoints } from 'lucide-react';
import { routingService, SearchResult } from '../services/routingService';
import { RouteResponse } from '../data/types';

interface RoutingPanelProps {
  onRouteCalculated: (
    route: RouteResponse,
    source: [number, number],
    destination: [number, number]
  ) => void;
  onClose: () => void;
}

export default function RoutingPanel({ onRouteCalculated, onClose }: RoutingPanelProps) {
  const [sourceQuery, setSourceQuery] = useState('');
  const [destQuery, setDestQuery] = useState('');
  const [sourceResults, setSourceResults] = useState<SearchResult[]>([]);
  const [destResults, setDestResults] = useState<SearchResult[]>([]);
  const [showSourceResults, setShowSourceResults] = useState(false);
  const [showDestResults, setShowDestResults] = useState(false);
  const [selectedSource, setSelectedSource] = useState<SearchResult | null>(null);
  const [selectedDest, setSelectedDest] = useState<SearchResult | null>(null);
  const [currentRoute, setCurrentRoute] = useState<RouteResponse | null>(null);
  const [isSearching, setIsSearching] = useState(false);
  const [isCalculating, setIsCalculating] = useState(false);

  const handleSourceSearch = async (value: string) => {
    setSourceQuery(value);
    if (value.length > 1) {
      setIsSearching(true);
      try {
        const results = await routingService.searchLocation(value);
        setSourceResults(results);
        setShowSourceResults(true);
      } catch (error) {
        console.error('Search error:', error);
        setSourceResults([]);
      } finally {
        setIsSearching(false);
      }
    } else {
      setShowSourceResults(false);
      setSourceResults([]);
    }
  };

  const handleDestSearch = async (value: string) => {
    setDestQuery(value);
    if (value.length > 1) {
      setIsSearching(true);
      try {
        const results = await routingService.searchLocation(value);
        setDestResults(results);
        setShowDestResults(true);
      } catch (error) {
        console.error('Search error:', error);
        setDestResults([]);
      } finally {
        setIsSearching(false);
      }
    } else {
      setShowDestResults(false);
      setDestResults([]);
    }
  };

  const handleSourceSelect = (result: SearchResult) => {
    setSourceQuery(result.name);
    setSelectedSource(result);
    setShowSourceResults(false);
  };

  const handleDestSelect = (result: SearchResult) => {
    setDestQuery(result.name);
    setSelectedDest(result);
    setShowDestResults(false);
  };

  const handleCalculateRoute = async () => {
    if (selectedSource && selectedDest) {
      setIsCalculating(true);
      try {
        const route = await routingService.calculateRoute(
          { lat: selectedSource.lat, lng: selectedSource.lng },
          { lat: selectedDest.lat, lng: selectedDest.lng }
        );
        setCurrentRoute(route);
        onRouteCalculated(
          route,
          [selectedSource.lat, selectedSource.lng],
          [selectedDest.lat, selectedDest.lng]
        );
      } catch (error) {
        console.error('Route calculation error:', error);
        alert('خطا در محاسبه مسیر. لطفا دوباره تلاش کنید.');
      } finally {
        setIsCalculating(false);
      }
    }
  };

  const getResultIcon = (type: string) => {
    switch (type) {
      case 'facility':
        return <Building2 className="w-5 h-5" />;
      case 'city':
      case 'province':
      case 'village':
        return <MapPinned className="w-5 h-5" />;
      default:
        return <MapPin className="w-5 h-5" />;
    }
  };

  const getResultTypeLabel = (type: string) => {
    switch (type) {
      case 'facility':
        return 'مکان';
      case 'city':
        return 'شهر';
      case 'province':
        return 'استان';
      case 'village':
        return 'روستا';
      default:
        return '';
    }
  };

  return (
    <div className="bg-white p-6">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-2">
          <Navigation className="w-7 h-7 text-blue-600 fill-current" />
          <h2 className="text-xl font-semibold text-gray-800">مسیریابی</h2>
        </div>
        <button
          onClick={onClose}
          className="text-gray-400 hover:text-gray-600 transition-colors"
        >
          <X className="w-6 h-6" />
        </button>
      </div>

      <div className="space-y-4 mb-6">
        <div className="relative">
          <label className="block text-sm font-bold text-gray-700 mb-2">مبدا</label>
          <div className="flex items-center px-3 gap-2 border border-gray-300 rounded-lg focus-within:outline-none focus-within:ring-2 focus-within:ring-green-500">
            <MapPin className="transform text-[#22c55e] w-5 h-5" />
            <input
              type="text"
              value={sourceQuery}
              onChange={(e) => handleSourceSearch(e.target.value)}
              placeholder="مبدا را وارد کنید..."
              className="w-full py-2 focus:outline-none"
            />
          </div>
          {showSourceResults && sourceResults.length > 0 && (
            <div className="absolute top-full mt-1 w-full bg-white rounded-lg shadow-lg border border-gray-200 max-h-60 overflow-y-auto z-50">
              {sourceResults.map((result, index) => (
                <button
                  key={index}
                  onClick={() => handleSourceSelect(result)}
                  className="w-full text-start px-4 py-3 hover:bg-gray-50 border-b border-gray-100 last:border-b-0 flex items-center gap-3"
                >
                  <div className="flex-shrink-0 mt-0.5 text-gray-500">
                    {getResultIcon(result.type)}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="font-bold text-gray-800 truncate">{result.name}</div>
                    <div className="flex items-center gap-2 mt-0.5">
                      <span className="text-xs font-bold text-blue-600">{getResultTypeLabel(result.type)}</span>
                      {result.address && (
                        <span className="text-xs text-gray-500 truncate">{result.address}</span>
                      )}
                    </div>
                  </div>
                </button>
              ))}
            </div>
          )}
        </div>

        <div className="relative">
          <label className="block text-sm font-bold text-gray-700 mb-2">مقصد</label>
          <div className="flex items-center px-3 gap-2 border border-gray-300 rounded-lg focus-within:outline-none focus-within:ring-2 focus-within:ring-green-500">
            <MapPin className="transform text-[#ef4444] w-5 h-5" />
            <input
              type="text"
              value={destQuery}
              onChange={(e) => handleDestSearch(e.target.value)}
              placeholder="مقصد را وارد کنید..."
              className="w-full py-2 focus:outline-none"
            />
          </div>
          {showDestResults && destResults.length > 0 && (
            <div className="absolute top-full mt-1 w-full bg-white rounded-lg shadow-lg border border-gray-200 max-h-60 overflow-y-auto z-50">
              {destResults.map((result, index) => (
                <button
                  key={index}
                  onClick={() => handleDestSelect(result)}
                  className="w-full text-start px-4 py-3 hover:bg-gray-50 border-b border-gray-100 last:border-b-0 flex items-center gap-3"
                >
                  <div className="flex-shrink-0 mt-0.5 text-gray-500">
                    {getResultIcon(result.type)}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="font-bold text-gray-800 truncate">{result.name}</div>
                    <div className="flex items-center gap-2 mt-0.5">
                      <span className="text-xs font-bold text-blue-600">{getResultTypeLabel(result.type)}</span>
                      {result.address && (
                        <span className="text-xs text-gray-500 truncate">{result.address}</span>
                      )}
                    </div>
                  </div>
                </button>
              ))}
            </div>
          )}
        </div>

        <button
          onClick={handleCalculateRoute}
          disabled={!selectedSource || !selectedDest || isCalculating}
          className="w-full flex items-center justify-center gap-2 bg-blue-600 text-white py-3 rounded-lg font-bold hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
        >
          <Waypoints className="w-6 h-6" />
          {isCalculating ? 'در حال محاسبه...' : 'محاسبه مسیر'}
        </button>
      </div>

      {currentRoute && currentRoute.routes && currentRoute.routes.length > 0 && (
        <div className="border-t pt-6">
          <div className="flex items-center justify-between mb-4 p-4 bg-green-50 rounded-lg">
            <div className="flex items-center gap-2">
              <Navigation className="w-5 h-5 text-green-600" />
              <span className="font-medium text-gray-800">
                {currentRoute.routes[0].legs[0].distance.text}
              </span>
            </div>
            <div className="flex items-center gap-2">
              <Clock className="w-5 h-5 text-green-600" />
              <span className="font-medium text-gray-800">
                {currentRoute.routes[0].legs[0].duration.text}
              </span>
            </div>
          </div>

          <h3 className="font-semibold text-gray-800 mb-3">مراحل مسیر</h3>
          <div className="space-y-3">
            {currentRoute.routes[0].legs[0].steps.map((step, index) => (
              <div key={index} className="flex items-center p-3 gap-3 bg-green-50 rounded-lg">
                <div className="flex-shrink-0 w-8 h-8 bg-green-600 text-white rounded-full flex items-end justify-center text-lg font-bold">
                  {index + 1}
                </div>
                <div className="flex-1">
                  <p className="text-gray-800 mb-1">{step.instruction || step.name}</p>
                  {step.distance.text && (
                    <div className="flex items-center text-sm text-gray-600">
                      <span>{step.distance.text}</span>
                      <ArrowLeft className="w-3 h-3 mx-2" />
                      <span>{step.duration.text}</span>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
