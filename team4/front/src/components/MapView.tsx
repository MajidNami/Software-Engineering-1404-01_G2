import { useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Popup, Polyline, useMap, ZoomControl } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { Place } from '../data/mockPlaces';
import polyline from "@mapbox/polyline";
import Routing from './Routing';
import { Star } from 'lucide-react';
import MapCenterListener from './MapCenterListener';

delete (L.Icon.Default.prototype as any)._getIconUrl;
L.Icon.Default.mergeOptions({
  // iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
  // iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  // shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
});

interface MapViewProps {
  places: Place[];
  center: [number, number];
  selectedPlace: Place | null;
  onPlaceSelect: (place: Place) => void;
  route: [number, number][] | null;
  sourceMarker: [number, number] | null;
  destinationMarker: [number, number] | null;
  onFindNearbyPlaces: (places: Place[]) => void;
}

function MapController({ center }: { center: [number, number] }) {
  const map = useMap();

  useEffect(() => {
    map.setView(center, map.getZoom());
  }, [center, map]);

  return null;
}

const createCustomIcon = (color: string) => {
  return L.divIcon({
    className: 'custom-marker',
    html: `
      <div style="
        background-color: ${color};
        width: 30px;
        height: 30px;
        border-radius: 50% 50% 50% 0;
        transform: rotate(-45deg);
        border: 3px solid white;
        box-shadow: 0 2px 5px rgba(0,0,0,0.3);
      ">
        <div style="
          width: 10px;
          height: 10px;
          background-color: white;
          border-radius: 50%;
          position: absolute;
          top: 50%;
          left: 50%;
          transform: translate(-50%, -50%);
        "></div>
      </div>
    `,
    iconSize: [30, 30],
    iconAnchor: [15, 30],
  });
};

export const sourceIcon = createCustomIcon('#22c55e');
export const destinationIcon = createCustomIcon('#ef4444');
const placesIcon = createCustomIcon("#0992c2");

export default function MapView({
  places,
  center,
  selectedPlace,
  onPlaceSelect,
  route,
  sourceMarker,
  destinationMarker,
  onFindNearbyPlaces
}: MapViewProps) {

  const decoded = polyline.decode(
    "kz{xEggtxHn@E|@iAtMcAq@k`Ap@yO_OyA"
  );

  return (
    <MapContainer
      center={center}
      zoom={12}
      zoomControl={false}
      style={{ height: '100%', width: '100%' }}
      className="z-0"
    >
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />
      <MapController center={center} />
      <ZoomControl position='bottomright' />
      {/* <Routing source={[40.7589, -73.9851]} destination={[40.7614, -73.9776]} /> */}

      {places.map((place) => (
        <Marker
          key={place.id}
          position={[place.latitude, place.longitude]}
          icon={placesIcon}
          eventHandlers={{
            click: () => onPlaceSelect(place),
          }}
        >
          <Popup>
            <div className="flex flex-col items-center gap-2 text-sm min-w-32">
              <h3 className="font-semibold mb-1">{place.name}</h3>
              <div className="flex gap-2 justify-center">
                <span className="inline-block px-3 py-1 bg-blue-100 text-blue-700 text-sm font-medium rounded-full uppercase">
                {place.category}
                </span>
                <div className="flex items-center bg-yellow-100 px-3 py-1 gap-1 w-fit rounded-full">
                  <Star className="w-5 h-5 text-yellow-500 fill-current" />
                  <span className="font-semibold text-gray-800">{place.rating}</span>
                </div>
              </div>
              <button
                className="w-full bg-blue-600 text-white py-2 rounded-full font-medium hover:bg-blue-700 transition-colors"
              >
                مسیریابی
              </button>
            </div>
          </Popup>
        </Marker>
      ))}

      {sourceMarker && (
        <Marker position={sourceMarker} icon={sourceIcon}>
          <Popup>
            <div className="text-sm text-center font-semibold">مبدا</div>
          </Popup>
        </Marker>
      )}

      {destinationMarker && (
        <Marker position={destinationMarker} icon={destinationIcon}>
          <Popup>
            <div className="text-sm text-center font-semibold">مقصد</div>
          </Popup>
        </Marker>
      )}

      {route && (
        <Polyline
          positions={route}
          color="#2845D6"
          weight={4}
        />
      )}

      {/* <Polyline positions={decoded} color='red'/> */}

      <MapCenterListener onFindPlaces={onFindNearbyPlaces} />
    </MapContainer>
  );
}
