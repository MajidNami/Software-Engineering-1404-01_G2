import { getApiUrl, API_CONFIG } from '../config/api';
import { Place, Review } from '../data/mockPlaces';
import { authHelper } from '../utils/authHelper';

interface City {
  city_id: number;
  name_fa?: string;
  name_en?: string;
  province?: {
    province_id: number;
    name_fa?: string;
    name_en?: string;
  };
  location?: {
    type: string;
    coordinates: [number, number];
  };
}

// Backend API response types
interface BackendFacility {
  fac_id: number;
  name_fa?: string;
  name_en?: string;
  category?: string | { name_en?: string; name_fa?: string };
  city?: City;
  province?: string | { name_en?: string; name_fa?: string };
  location?: {
    type: 'Point';
    coordinates: [number, number]; // [lng, lat]
  };
  avg_rating?: number;
  review_count: number;
  primary_image: string | null;
  price_from: {
    type: 'exact' | 'range';
    value?: number;
    min?: number;
    max?: number;
  } | null;
  price_tier: string;
  price_tier_display: string;
  is_24_hour: boolean;
  amenities: Array<{
    name_fa: string;
    name_en: string;
  }>;
}

interface BackendFacilityDetail extends BackendFacility {
  description_fa?: string;
  description_en?: string;
  address_fa?: string;
  address_en?: string;
  contact_number?: string;
  email?: string;
  website?: string;
  working_hours?: string;
  pricing?: Array<{
    pricing_id: number;
    price_type: string;
    price_type_display: string;
    price: number;
    description_fa: string;
    description_en: string;
  }>;
  images?: Array<{
    image_id: number;
    image_url: string;
    is_primary: boolean;
    alt_text: string;
  }>;
}

interface BackendReview {
  review_id: number;
  user_id: string;
  user_name?: string;
  rating: number;
  comment: string;
  created_at: string;
  updated_at: string;
}

interface FacilityListResponse {
  count: number;
  next: string | null;
  previous: string | null;
  results: BackendFacility[];
}

interface NearbyFacility {
  place: BackendFacility;
  distance_meters: number;
}

interface NearbyFacilityListResponse {
  count: number;
  next: string | null;
  previous: string | null;
  results: NearbyFacility[];
}

// Transform backend facility to frontend Place format
const transformFacilityToPlace = (facility: BackendFacility, reviews: Review[] = []): Place => {
  const [lng, lat] = facility.location?.coordinates || [0, 0];
  
  // Handle category - can be string or object
  const categoryStr = typeof facility.category === 'string' 
    ? facility.category 
    : facility.category?.name_en || 'unknown';
  
  // Safely build address with fallbacks
  const cityName = facility.city?.name_fa || facility.city?.name_en || 'Unknown';
  const provinceName = facility.city?.province?.name_fa || facility.city?.province?.name_en || '';
  const address = provinceName ? `${cityName}, ${provinceName}` : cityName;
  
  return {
    id: facility.fac_id.toString(),
    name: facility.name_en || facility.name_fa || 'Unknown',
    category: categoryStr.toLowerCase(),
    latitude: lat,
    longitude: lng,
    rating: facility.avg_rating || 0,
    address: address,
    description: facility.name_fa || facility.name_en || '',
    images: facility.primary_image ? [facility.primary_image] : [
      'https://images.pexels.com/photos/258154/pexels-photo-258154.jpeg?auto=compress&cs=tinysrgb&w=800'
    ],
    reviews: reviews,
  };
};

// Transform backend review to frontend Review format
const transformReview = (review: BackendReview): Review => {
  return {
    id: review.review_id.toString(),
    author: review.user_name || `User ${review.user_id}`,
    rating: review.rating,
    comment: review.comment,
    date: new Date(review.created_at).toISOString().split('T')[0],
  };
};

class PlacesService {
  /**
   * Fetch all facilities from backend
   */
  async getFacilities(params?: {
  category?: string;
  city?: string;
  province?: string;
  page?: number;
  page_size?: number;
}): Promise<Place[]> {
  try {
    const url = new URL(getApiUrl(API_CONFIG.ENDPOINTS.FACILITIES));

    // Add query parameters
    if (params?.page) {
      url.searchParams.append('page', params.page.toString());
    }

    // Optional page_size
    if (params?.page_size) {
      url.searchParams.append('page_size', params.page_size.toString());
    }

    let allFacilities: BackendFacility[] = [];
    let nextUrl: string | null = url.toString();

    while (nextUrl) {
      const response = await fetch(nextUrl, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data: FacilityListResponse = await response.json();

      // Collect results
      allFacilities = [...allFacilities, ...data.results];

      // Move to next page
      nextUrl = data.next;
    }

    // Transform everything at the end
    return allFacilities.map(facility =>
      transformFacilityToPlace(facility)
    );

  } catch (error) {
    console.error('Error fetching all facilities:', error);
    return [];
  }
}

  /**
   * Fetch facilities with filters (using POST for complex queries)
   */
  async searchFacilities(filters: {
    category?: string;
    city?: string;
    province?: string;
    village?: string;
    amenity?: string;
    price_tier?: string;
    min_rating?: number;
    is_24_hour?: boolean;
  }): Promise<Place[]> {
    try {
      const url = getApiUrl(API_CONFIG.ENDPOINTS.FACILITIES) + "search/";

      const response = await fetch(url, {
        method: 'POST',
        headers: authHelper.getAuthHeaders(),
        credentials: 'include',
        body: JSON.stringify(filters),
      });

      let allFacilities: BackendFacility[] = [];
      let nextUrl: string | null = url.toString();

      while (nextUrl) {
        const response = await fetch(nextUrl, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(filters),
        });

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data: FacilityListResponse = await response.json();

        // Collect results
        allFacilities = [...allFacilities, ...data.results];

        // Move to next page
        nextUrl = data.next;
      }

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      return allFacilities.map(facility => transformFacilityToPlace(facility));
    } catch (error) {
      console.error('Error searching facilities:', error);
      return [];
    }
  }

  /**
   * Fetch single facility details with reviews
   */
  async getFacilityDetails(facilityId: string): Promise<Place | null> {
    try {
      const facilityUrl = getApiUrl(`${API_CONFIG.ENDPOINTS.FACILITIES}${facilityId}/`);
      
      const facilityResponse = await fetch(facilityUrl, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
      });

      if (!facilityResponse.ok) {
        throw new Error(`HTTP error! status: ${facilityResponse.status}`);
      }

      const facility: BackendFacilityDetail = await facilityResponse.json();
      
      // Fetch reviews for this facility
      const reviews = await this.getFacilityReviews(facilityId);
      
      // Add all images if available
      const images = facility.images?.map(img => img.image_url) || [];
      if (images.length === 0 && facility.primary_image) {
        images.push(facility.primary_image);
      }
      
      const place = transformFacilityToPlace(facility, reviews);
      
      // Enhance with detail information
      return {
        ...place,
        description: facility.description_en || facility.description_fa || place.description,
        address: facility.address_en || facility.address_fa || place.address,
        images: images.length > 0 ? images : place.images,
      };
    } catch (error) {
      console.error('Error fetching facility details:', error);
      return null;
    }
  }

  /**
   * Fetch reviews for a facility
   */
  async getFacilityReviews(facilityId: string): Promise<Review[]> {
    try {
      const url = new URL(getApiUrl(API_CONFIG.ENDPOINTS.REVIEWS));
      url.searchParams.append('facility_id', facilityId);

      const response = await fetch(url.toString(), {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data: { results: BackendReview[] } = await response.json();
      
      return data.results.map(transformReview);
    } catch (error) {
      console.error('Error fetching reviews:', error);
      return [];
    }
  }

  /**
   * Fetch facilities by category
   */
  async getFacilitiesByCategory(category: string): Promise<Place[]> {
    return this.searchFacilities({ category });
  }

  /**
   * Search facilities by name
   */
  async searchByName(name: string): Promise<Array<{ name: string; lat: number; lng: number; fac_id: number }>> {
    try {
      const url = `${API_CONFIG.BASE_URL}${API_CONFIG.TEAM_PREFIX}/api/facilities/search/`;
      
      const response = await fetch(url, {
        method: 'POST',
        headers: authHelper.getAuthHeaders(),
        credentials: 'include',
        body: JSON.stringify({ name }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data: { results: BackendFacility[] } = await response.json();
      
      // Transform to search result format
      return data.results.map(facility => ({
        name: facility.name_fa || facility.name_en || 'Unknown',
        lat: facility.location?.coordinates?.[1] || 0, // latitude
        lng: facility.location?.coordinates?.[0] || 0, // longitude
        fac_id: facility.fac_id
      }));
    } catch (error) {
      console.error('Error searching facilities:', error);
      return [];
    }
  }

  // fetch nearby facilities
  async getNearbyFacilities(params: {
    lat: number;
    lng: number;
    radius: number;
    categories?: string[];
    price_tiers?: string[];
    page?: number;
    page_size?: number;
  }): Promise<Place[]> {
    try {
      const url = new URL(getApiUrl(API_CONFIG.ENDPOINTS.FACILITIES) + "nearby/");

      url.searchParams.append('lat', params.lat.toString());
      url.searchParams.append('lng', params.lng.toString());
      url.searchParams.append('radius', params.radius.toString());
      
      // Add query parameters
      if (params?.page) {
        url.searchParams.append('page', params.page.toString());
      }
      if (params?.page_size) {
        url.searchParams.append('page_size', params.page_size.toString());
      }

      const response = await fetch(url.toString(), {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data: NearbyFacilityListResponse = await response.json();
      console.log(data);
      
      // Transform backend data to frontend format
      return data.results.map(facility => transformFacilityToPlace(facility.place));
    } catch (error) {
      console.error('Error fetching facilities:', error);
      // Return empty array on error instead of throwing
      return [];
    }
  }
}

export const placesService = new PlacesService();
export default placesService;
