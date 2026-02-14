import { API_CONFIG } from '../config/api';
import { authHelper } from '../utils/authHelper';
import { RouteResponse } from '../data/types';

const NAVIGATION_URL = `${API_CONFIG.BASE_URL}${API_CONFIG.TEAM_PREFIX}/api/navigation/route/`;
const REGIONS_URL = `${API_CONFIG.BASE_URL}${API_CONFIG.TEAM_PREFIX}/api/regions/search`;
const FACILITIES_URL = `${API_CONFIG.BASE_URL}${API_CONFIG.TEAM_PREFIX}/api/facilities`;

export interface SearchResult {
  id: string | number;
  name: string;
  type: 'facility' | 'city' | 'province' | 'village';
  lat: number;
  lng: number;
  address?: string;
  category?: string;
}

export const routingService = {
  /**
   * Search for both facilities and regions
   */
  async searchLocation(query: string): Promise<SearchResult[]> {
    if (!query || query.length < 2) {
      return [];
    }

    try {
      const [regionsResponse, facilitiesResponse] = await Promise.all([
        // Search regions (cities, provinces, villages)
        fetch(`${REGIONS_URL}?query=${encodeURIComponent(query)}`, {
          credentials: 'include'
        }).then(res => 
          res.ok ? res.json() : { regions: [] }
        ),
        // Search facilities by name
        fetch(`${FACILITIES_URL}/search/`, {
          method: 'POST',
          headers: authHelper.getAuthHeaders(),
          credentials: 'include',
          body: JSON.stringify({
            name: query
          })
        }).then(res => res.ok ? res.json() : { results: [] })
      ]);

      const results: SearchResult[] = [];
/*
      // Add region results
      if (regionsResponse.regions) {
        for (const region of regionsResponse.regions) {
          results.push({
            id: region.id,
            name: region.name,
            type: 'city', // Regions from API
            lat: 0, // TODO: Backend should provide lat/lng for regions
            lng: 0,
            address: region.parent_region_name
          });
        }
      }
*/
      // Add facility results
      if (facilitiesResponse.results) {
        const facilities = facilitiesResponse.results;

        for (const facility of facilities) {
          if (facility.location && facility.location.coordinates) {
            results.push({
              id: facility.fac_id,
              name: facility.name_fa || facility.name_en,
              type: 'facility',
              lat: facility.location.coordinates[1],
              lng: facility.location.coordinates[0],
              address: `${facility.city || ''}, ${facility.province || ''}`.trim(),
              category: facility.category
            });
          }
        }
      }

      // Remove duplicates and sort by relevance
      return results
        .filter((result, index, self) => 
          index === self.findIndex(r => r.id === result.id)
        )
        .slice(0, 10);

    } catch (error) {
      console.error('Search error:', error);
      return [];
    }
  },

  /**
   * Calculate route between two points
   */
  async calculateRoute(
    origin: { lat: number; lng: number },
    destination: { lat: number; lng: number },
    type: 'car' | 'motorcycle' = 'car',
    options?: {
      avoidTrafficZone?: boolean;
      avoidOddEvenZone?: boolean;
      alternative?: boolean;
    }
  ): Promise<RouteResponse> {
    const response = await fetch(NAVIGATION_URL, {
      method: 'POST',
      headers: authHelper.getAuthHeaders(),
      credentials: 'include',
      body: JSON.stringify({
        type,
        origin: `${origin.lat},${origin.lng}`,
        destination: `${destination.lat},${destination.lng}`,
        avoidTrafficZone: options?.avoidTrafficZone || false,
        avoidOddEvenZone: options?.avoidOddEvenZone || false,
        alternative: options?.alternative || false
      })
    });

    if (!response.ok) {
      throw new Error('Failed to calculate route');
    }

    return response.json();
  },

  /**
   * Format distance text
   */
  formatDistance(meters: number): string {
    if (meters < 1000) {
      return `${Math.round(meters)} متر`;
    }
    return `${(meters / 1000).toFixed(1)} کیلومتر`;
  },

  /**
   * Format duration text
   */
  formatDuration(seconds: number): string {
    const minutes = Math.floor(seconds / 60);
    const hours = Math.floor(minutes / 60);
    const remainingMinutes = minutes % 60;

    if (hours > 0) {
      return `${hours} ساعت و ${remainingMinutes} دقیقه`;
    }
    return `${minutes} دقیقه`;
  }
};
