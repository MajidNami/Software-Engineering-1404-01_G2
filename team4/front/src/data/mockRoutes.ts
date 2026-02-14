export interface RouteStep {
  instruction: string;
  distance: string;
  duration: string;
}

export interface Route {
  coordinates: [number, number][];
  distance: string;
  duration: string;
  steps: RouteStep[];
}

export const calculateRoute = (
  source: [number, number],
  destination: [number, number]
): Route => {
  const midLat = (source[0] + destination[0]) / 2;
  const midLng = (source[1] + destination[1]) / 2;

  const coordinates: [number, number][] = [
    source,
    [midLat + 0.002, midLng - 0.003],
    [midLat - 0.001, midLng + 0.002],
    [midLat + 0.003, midLng + 0.001],
    destination,
  ];

  const distance = Math.sqrt(
    Math.pow(destination[0] - source[0], 2) + Math.pow(destination[1] - source[1], 2)
  );

  const distanceKm = (distance * 111).toFixed(1);
  const durationMin = Math.ceil(parseFloat(distanceKm) * 3);

  return {
    coordinates,
    distance: `${distanceKm} km`,
    duration: `${durationMin} min`,
    steps: [
      {
        instruction: 'Head north on your current street',
        distance: '0.3 km',
        duration: '2 min',
      },
      {
        instruction: 'Turn right onto Main Avenue',
        distance: '0.8 km',
        duration: '4 min',
      },
      {
        instruction: 'Continue straight for 2 blocks',
        distance: '0.5 km',
        duration: '3 min',
      },
      {
        instruction: 'Turn left onto Park Street',
        distance: '0.6 km',
        duration: '3 min',
      },
      {
        instruction: 'Your destination will be on the right',
        distance: '0.2 km',
        duration: '1 min',
      },
    ],
  };
};

export const searchLocation = (query: string): { name: string; lat: number; lng: number }[] => {
  const locations = [
    { name: 'Times Square, New York', lat: 40.7580, lng: -73.9855 },
    { name: 'Empire State Building, New York', lat: 40.7484, lng: -73.9857 },
    { name: 'Central Park, New York', lat: 40.7829, lng: -73.9654 },
    { name: 'Brooklyn Bridge, New York', lat: 40.7061, lng: -73.9969 },
    { name: 'Statue of Liberty, New York', lat: 40.6892, lng: -74.0445 },
    { name: 'Grand Central Terminal, New York', lat: 40.7527, lng: -73.9772 },
    { name: 'Metropolitan Museum of Art, New York', lat: 40.7794, lng: -73.9632 },
    { name: 'Rockefeller Center, New York', lat: 40.7587, lng: -73.9787 },
  ];

  if (!query) return locations;

  return locations.filter((loc) =>
    loc.name.toLowerCase().includes(query.toLowerCase())
  );
};
