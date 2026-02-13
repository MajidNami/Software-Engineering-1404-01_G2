import { LatLng } from "leaflet";
import { useRef, useState } from "react";
import { useMapEvents } from "react-leaflet";
import { Place } from "../data/mockPlaces";
import { Search } from "lucide-react";
import placesService from "../services/placesService";

interface Props {
  onFindPlaces: (places: Place[]) => void;
}

const MapCenterListener = ({ onFindPlaces }: Props) => {
  const [showButton, setShowButton] = useState(false);
  const [loading, setLoading] = useState(false);
  const centerRef = useRef<LatLng | null>(null);
  const [center, setCenter] = useState<LatLng | null>(null);

  const map = useMapEvents({
    moveend() {
      centerRef.current = map.getCenter();
      setCenter(map.getCenter());
      setShowButton(true);
    },
  });

  return (
    <div className="absolute z-[1000] w-full h-full p-5 pointer-events-none flex justify-center items-end">
      {showButton && (
        <button
          className="flex gap-2 items-center bg-white pointer-events-auto py-3 px-4 border-2 border-gray-200 rounded-full font-bold"
          onClick={async () => {
            setLoading(true);
            const foundPlaces = await placesService.getNearbyFacilities(
              {
                lat: center ? center.lat : 0,
                lng: center ? center.lng : 0,
                radius: 20000
              }
            );

            onFindPlaces(foundPlaces);
            console.log(foundPlaces);
            setShowButton(false);
            setLoading(false);
          }}
        >
          <Search className="text-green-500 w-6 h-6" />
          {loading ? (
            <>
              جستجوی منطقه...
              <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-green-600"></div>
            </>
          ) : (
            "جستجوی این منطقه"
          )}
        </button>
      )}
    </div>
  );
};

export default MapCenterListener;
