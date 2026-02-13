// API Configuration
export const API_CONFIG = {
  BASE_URL: '',  // Empty for same-origin requests (served from Django)
  TEAM_PREFIX: '/team4',
  ENDPOINTS: {
    FACILITIES: '/api/facilities/',
    CATEGORIES: '/api/categories/',
    FAVORITES: '/api/favorites/',
    REVIEWS: '/api/reviews/',
  },
};

export const getApiUrl = (endpoint: string): string => {
  return `${API_CONFIG.BASE_URL}${API_CONFIG.TEAM_PREFIX}${endpoint}`;
};
