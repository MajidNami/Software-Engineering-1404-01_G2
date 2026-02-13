/**
 * Authentication helper utilities
 * 
 * Uses cookies for authentication tokens (access_token)
 * Backend sets HttpOnly cookies, but we try to read if accessible
 */

/**
 * Get a specific cookie value by name
 */
function getCookie(name: string): string | null {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) {
    const cookieValue = parts.pop()?.split(';').shift();
    return cookieValue || null;
  }
  return null;
}

/**
 * Get CSRF token from cookies
 */
function getCSRFToken(): string {
  return getCookie('csrftoken') || '';
}

export const authHelper = {
  /**
   * Get authentication token from cookie
   * Returns null if not found or if cookie is HttpOnly (not accessible from JS)
   */
  getToken(): string | null {
    // Try to get access_token from cookie
    // Note: If backend sets HttpOnly=true, this will return null
    // which is fine - cookie will still be sent automatically with requests
    return null;
  },

  /**
   * Set authentication token
   * Note: Backend should handle setting cookies via Set-Cookie header
   */
  setToken(token: string): void {
    // Store in localStorage as fallback
    localStorage.setItem('auth_token', token);
    
  },

  /**
   * Remove authentication token (logout)
   */
  removeToken(): void {
    localStorage.removeItem('auth_token');
    // Note: Can't remove HttpOnly cookies from JavaScript
    // Backend should handle this on logout
  },

  /**
   * Check if user is authenticated
   */
  isAuthenticated(): boolean {
    return !!this.getToken();
  },

  /**
   * Get CSRF token from cookie
   */
  getCSRFToken(): string {
    return getCSRFToken();
  },

  /**
   * Get headers with authentication token and CSRF token
   */
  getAuthHeaders(): HeadersInit {
    const token = this.getToken();
    const csrfToken = getCSRFToken();
    
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
    };

    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    if (csrfToken) {
      headers['X-CSRFToken'] = csrfToken;
    }

    return headers;
  }
};

