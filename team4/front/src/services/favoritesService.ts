import { API_CONFIG } from '../config/api';
import { authHelper } from '../utils/authHelper';

const FAVORITES_URL = `${API_CONFIG.BASE_URL}${API_CONFIG.TEAM_PREFIX}/api/favorites`;

export interface FavoriteToggleResponse {
  status: 'added' | 'removed';
  favorited: boolean;
}

export interface FavoriteCheckResponse {
  is_favorite: boolean;
  facility_id: string;
}

export interface FavoritePlace {
  favorite_id: number;
  user_id: number;
  facility: number;
  facility_detail: {
    fac_id: number;
    name_fa: string;
    name_en: string;
    category: string;
    city: string;
    province: string;
    location: {
      type: string;
      coordinates: [number, number];
    };
    avg_rating: string;
    review_count: number;
    primary_image: string | null;
    price_from: any;
    price_tier: string;
    price_tier_display: string;
    is_24_hour: boolean;
    amenities: any[];
  };
  created_at: string;
}


export const favoritesService = {
  /**
   * Toggle favorite status for a facility
   */
  async toggleFavorite(facilityId: number): Promise<FavoriteToggleResponse> {
    
    const response = await fetch(`${FAVORITES_URL}/toggle/`, {
      method: 'POST',
      headers: authHelper.getAuthHeaders(),
      credentials: 'include',
      body: JSON.stringify({
        facility: facilityId
      })
    });

    if (!response.ok) {
      throw new Error('Failed to toggle favorite');
    }

    return response.json();
  },

  /**
   * Check if a facility is favorited
   */
  async checkFavorite(facilityId: number): Promise<boolean> {
    const response = await fetch(`${FAVORITES_URL}/check/?facility=${facilityId}`, {
      method: 'GET',
      headers: authHelper.getAuthHeaders(),
      credentials: 'include'
    });

    if (!response.ok) {
      throw new Error('Failed to check favorite status');
    }

    const data: FavoriteCheckResponse = await response.json();
    return data.is_favorite;
  },

  /**
   * Get all user favorites
   */
  async getFavorites(): Promise<FavoritePlace[]> {
    const response = await fetch(FAVORITES_URL, {
      method: 'GET',
      headers: authHelper.getAuthHeaders(),
      credentials: 'include'
    });

    if (!response.ok) {
      throw new Error('Failed to fetch favorites');
    }

    const data = await response.json();
    // API returns paginated response with results array
    return data.results || [];
  }
};
