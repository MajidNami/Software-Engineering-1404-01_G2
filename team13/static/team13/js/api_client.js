/**
 * Team 13 API Client — Places, Events, Routes, Emergency.
 * Appends format=json to all requests. CSRF helper for POST (rating).
 */

/** مسیر پایهٔ API تیم ۱۳ — همیشه به صورت مطلق مثلاً /team13 تا درخواست‌ها به بک‌اند درست بروند */
const API_BASE = (window.TEAM13_API_BASE || '/team13').replace(/\/$/, '');

/**
 * Get CSRF token from cookie (Django's csrftoken cookie).
 * @returns {string|null}
 */
function getCsrfToken() {
  const name = 'csrftoken';
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === name + '=') {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

/**
 * Fetch JSON from a team13 endpoint. Automatically appends format=json.
 * @param {string} endpoint - Path relative to API_BASE, e.g. 'places/' or 'routes/'
 * @param {Record<string, string>} [params] - Optional query params (merged with format=json)
 * @returns {Promise<object>} Parsed JSON
 */
async function fetchData(endpoint, params = {}) {
  const path = endpoint.startsWith('http') ? endpoint : API_BASE + '/' + (endpoint || '').replace(/^\//, '');
  const url = new URL(path, window.location.origin);
  const query = { format: 'json', ...params };
  Object.keys(query).forEach(key => {
    if (query[key] != null && query[key] !== '') url.searchParams.set(key, query[key]);
  });
  const res = await fetch(url.toString(), {
    method: 'GET',
    headers: { Accept: 'application/json' },
    credentials: 'same-origin',
  });
  if (!res.ok) throw new Error(`HTTP ${res.status}: ${res.statusText}`);
  return res.json();
}

/**
 * POST for rating (place or event). Sends CSRF via header and form body.
 * @param {string} url - Path relative to API_BASE, e.g. places/<uuid>/rate/
 * @param {{ rating: number }} data - e.g. { rating: 5 }
 * @returns {Promise<Response>}
 */
async function postRating(url, data) {
  const csrf = getCsrfToken();
  const body = new URLSearchParams(data);
  if (csrf) body.append('csrfmiddlewaretoken', csrf);
  const fullUrl = url.startsWith('http') ? url : API_BASE + '/' + (url || '').replace(/^\//, '');
  return fetch(fullUrl, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
      'X-CSRFToken': csrf || '',
      'Accept': 'application/json',
    },
    body: body.toString(),
    credentials: 'same-origin',
  });
}

/**
 * POST JSON to an endpoint (e.g. map-matching). Sends CSRF via header.
 */
async function postJson(endpoint, data) {
  const csrf = getCsrfToken();
  const fullUrl = endpoint.startsWith('http') ? endpoint : API_BASE + '/' + (endpoint || '').replace(/^\//, '');
  const res = await fetch(fullUrl, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': csrf || '',
      'Accept': 'application/json',
    },
    body: JSON.stringify(data),
    credentials: 'same-origin',
  });
  if (!res.ok) throw new Error('HTTP ' + res.status + ': ' + res.statusText);
  return res.json();
}

// Convenience API names — مسیرها نسبی به API_BASE (مثلاً /team13)
const api = {
  places: (params) => fetchData('places/', params),
  placeDetail: (placeId) => fetchData(`places/${placeId}/`),
  placeRate: (placeId, rating) => postRating(`places/${placeId}/rate/`, { rating }),
  events: (params) => fetchData('events/', params || {}),
  eventDetail: (eventId) => fetchData(`events/${eventId}/`),
  eventRate: (eventId, rating) => postRating(`events/${eventId}/rate/`, { rating }),
  routes: (sourcePlaceId, destinationPlaceId, travelMode = 'car', options = {}) => {
    const params = {
      source_place_id: sourcePlaceId,
      destination_place_id: destinationPlaceId,
      travel_mode: travelMode,
    };
    if (options.no_traffic) params.no_traffic = '1';
    if (options.bearing != null && options.bearing >= 0 && options.bearing <= 360) params.bearing = String(options.bearing);
    if (options.avoid_traffic_zone) params.avoid_traffic_zone = '1';
    if (options.avoid_odd_even_zone) params.avoid_odd_even_zone = '1';
    if (options.alternative) params.alternative = '1';
    return fetchData('routes/', params);
  },
  emergency: (lat, lon, limit = 50, radiusKm = 10) => {
    const params = { lat: String(lat), lon: String(lon), limit: String(limit), radius_km: String(radiusKm) };
    return fetchData('emergency/', params);
  },
  tsp: (waypoints, options = {}) => {
    const params = {};
    if (Array.isArray(waypoints) && waypoints.length >= 2) {
      params.waypoints = waypoints.map(w => (Array.isArray(w) ? w[0] + ',' + w[1] : (w.lat + ',' + w.lng))).join('|');
    } else if (typeof waypoints === 'string' && waypoints.indexOf('|') !== -1) {
      params.waypoints = waypoints;
    } else {
      return Promise.reject(new Error('waypoints باید آرایه‌ای از حداقل دو نقطه [lat,lng] یا رشتهٔ lat,lng|lat,lng باشد'));
    }
    if (options.round_trip !== undefined) params.round_trip = options.round_trip ? '1' : '0';
    if (options.source_is_any_point !== undefined) params.source_is_any_point = options.source_is_any_point ? '1' : '0';
    if (options.last_is_any_point !== undefined) params.last_is_any_point = options.last_is_any_point ? '1' : '0';
    return fetchData('tsp/', params);
  },
  distanceMatrix: (origins, destinations, options = {}) => {
    const toStr = (points) => {
      if (typeof points === 'string') return points;
      if (Array.isArray(points) && points.length > 0) {
        return points.map(p => (Array.isArray(p) ? p[0] + ',' + p[1] : (p.lat + ',' + p.lng))).join('|');
      }
      return '';
    };
    const o = toStr(origins);
    const d = toStr(destinations);
    if (!o || !d) return Promise.reject(new Error('origins و destinations الزامی هستند (آرایه یا رشتهٔ lat,lng|...)'));
    const params = { origins: o, destinations: d };
    if (options.type === 'motorcycle') params.type = 'motorcycle';
    if (options.no_traffic) params.no_traffic = '1';
    return fetchData('distance-matrix/', params);
  },
  isochrone: (lat, lng, options = {}) => {
    const params = { lat: String(lat), lng: String(lng) };
    if (options.distance_km != null) params.distance = String(options.distance_km);
    if (options.time_minutes != null) params.time = String(options.time_minutes);
    if (options.polygon) params.polygon = '1';
    if (options.denoise != null && options.denoise >= 0 && options.denoise <= 1) params.denoise = String(options.denoise);
    if (params.distance === undefined && params.time === undefined) return Promise.reject(new Error('حداقل distance_km یا time_minutes الزامی است'));
    return fetchData('isochrone/', params);
  },
  search: (term, options = {}) => {
    const params = { q: String(term || '').trim() };
    if (params.q === '') return Promise.resolve({ count: 0, items: [] });
    if (options.lat != null && options.lng != null) { params.lat = String(options.lat); params.lng = String(options.lng); }
    if (options.limit != null) params.limit = String(Math.min(30, Math.max(1, Number(options.limit))));
    return fetchData('neshan-search/', params);
  },
  /**
   * تبدیل آدرس متنی به مختصات (Geocoding) نشان.
   * @param {string} address - آدرس مورد نظر
   * @param {{ province?: string, city?: string, lat?: number, lng?: number, plus?: boolean, extent?: { southWest: {latitude,longitude}, northEast: {latitude,longitude} } }} [options]
   * @returns {Promise<{ items: Array<{ location: { latitude, longitude }, province, city, neighbourhood, unMatchedTerm }> }>}
   */
  geocode: (address, options = {}) => {
    const params = { address: String(address || '').trim() };
    if (params.address === '') return Promise.resolve({ items: [] });
    if (options.province) params.province = String(options.province);
    if (options.city) params.city = String(options.city);
    if (options.lat != null && options.lng != null) {
      params.lat = String(options.lat);
      params.lng = String(options.lng);
    }
    if (options.plus) params.plus = '1';
    if (options.extent && options.extent.southWest && options.extent.northEast) {
      const sw = options.extent.southWest;
      const ne = options.extent.northEast;
      params.sw_lat = String(sw.latitude);
      params.sw_lng = String(sw.longitude);
      params.ne_lat = String(ne.latitude);
      params.ne_lng = String(ne.longitude);
    }
    return fetchData('geocode/', params);
  },
  mapMatching: (path) => {
    let pathStr;
    if (typeof path === 'string') {
      pathStr = path.trim();
      if (pathStr.indexOf('|') === -1) return Promise.reject(new Error('path باید حداقل دو نقطه به صورت lat,lng|lat,lng داشته باشد'));
    } else if (Array.isArray(path) && path.length >= 2) {
      pathStr = path.map(p => (Array.isArray(p) ? p[0] + ',' + p[1] : (p.lat + ',' + p.lng))).join('|');
    } else {
      return Promise.reject(new Error('path باید رشتهٔ lat,lng|... یا آرایهٔ حداقل دو نقطه باشد'));
    }
    return postJson('map-matching/', { path: pathStr });
  },
};

const INITIAL_PLACES_LIMIT = 2000;   // بار اول حداکثر این تعداد مکان
const PLACES_PAGE_SIZE = 300;
const LOAD_MORE_CHUNK = 500;         // هر بار «بار بیشتر» چند مکان اضافه شود

/**
 * بار اول: تا INITIAL_PLACES_LIMIT مکان و همهٔ رویدادها را می‌گیرد و در کش نگه می‌دارد.
 * اگر کش وجود داشته باشد دوباره جستجو نمی‌کند مگر forceRefresh true باشد.
 * @param {boolean} [forceRefresh=false]
 * @returns {Promise<{ places: Array, events: Array }>}
 */
async function loadMapData(forceRefresh = false) {
  if (!forceRefresh && window._team13PlacesCache && window._team13EventsCache != null) {
    return {
      places: window._team13PlacesCache,
      events: window._team13EventsCache,
    };
  }
  const baseUrl = window.location.origin + (API_BASE || '/team13');
  let allPlaces = [];
  let page = 1;
  let hasMore = true;
  while (hasMore && allPlaces.length < INITIAL_PLACES_LIMIT) {
    const placesRes = await fetch(
      `${baseUrl}/places/?format=json&page=${page}&page_size=${PLACES_PAGE_SIZE}`,
      { method: 'GET', headers: { Accept: 'application/json' }, credentials: 'same-origin' }
    );
    if (!placesRes.ok) throw new Error('Places fetch failed: ' + placesRes.status);
    const placesData = await placesRes.json();
    const chunk = placesData.places || [];
    allPlaces = allPlaces.concat(chunk);
    hasMore = placesData.has_more === true && chunk.length === PLACES_PAGE_SIZE && allPlaces.length < INITIAL_PLACES_LIMIT;
    page += 1;
  }
  window._team13PlacesCache = allPlaces.slice(0, INITIAL_PLACES_LIMIT);
  window._team13PlacesNextPage = page;

  const eventsRes = await fetch(`${baseUrl}/events/?format=json`, { method: 'GET', headers: { Accept: 'application/json' }, credentials: 'same-origin' });
  if (!eventsRes.ok) throw new Error('Events fetch failed: ' + eventsRes.status);
  const eventsData = await eventsRes.json();
  window._team13EventsCache = eventsData.events || [];
  return {
    places: window._team13PlacesCache,
    events: window._team13EventsCache,
  };
}

/**
 * بار بعدی مکان‌ها را از سرور می‌گیرد و به کش اضافه می‌کند (به مرور زمان افزایش تعداد آیکون‌ها).
 * @returns {Promise<{ places: Array, added: number }>} کل کش مکان‌ها و تعداد تازه‌اضافه‌شده
 */
async function loadMoreMapPlaces() {
  const baseUrl = window.location.origin + (API_BASE || '/team13');
  const cache = window._team13PlacesCache || [];
  const startPage = window._team13PlacesNextPage != null ? window._team13PlacesNextPage : 1;
  const existingIds = new Set(cache.map((p) => (p.place_id || p.id || '').toString()));
  let added = [];
  let page = startPage;
  let hasMore = true;
  const maxToAdd = LOAD_MORE_CHUNK;
  while (hasMore && added.length < maxToAdd) {
    const placesRes = await fetch(
      `${baseUrl}/places/?format=json&page=${page}&page_size=${PLACES_PAGE_SIZE}`,
      { method: 'GET', headers: { Accept: 'application/json' }, credentials: 'same-origin' }
    );
    if (!placesRes.ok) break;
    const placesData = await placesRes.json();
    const chunk = placesData.places || [];
    for (const p of chunk) {
      const id = (p.place_id || p.id || '').toString();
      if (!existingIds.has(id)) {
        existingIds.add(id);
        added.push(p);
        if (added.length >= maxToAdd) break;
      }
    }
    hasMore = placesData.has_more === true && chunk.length === PLACES_PAGE_SIZE;
    page += 1;
  }
  window._team13PlacesNextPage = page;
  if (added.length > 0) {
    window._team13PlacesCache = (window._team13PlacesCache || []).concat(added);
  }
  return { places: window._team13PlacesCache, added: added.length };
}

/**
 * مسیریابی و ETA از بک‌اند (Haversine). خط مسیر فعلاً مستقیم (مبدأ–مقصد)؛ بعداً با API جدید جایگزین می‌شود.
 */
function toTravelMode(serviceType) {
  const mode = String(serviceType).toLowerCase();
  if (mode === 'walking') return 'walk';
  if (mode === 'bicycle') return 'bicycle';
  if (mode === 'transit') return 'transit';
  return 'car';
}

/**
 * استخراج مختصات مسیر از پاسخ مسیریابی نشان (overview_polyline یا legs[].steps[].polyline).
 * مستندات: https://platform.neshan.org/docs/sdk/web/mapboxgl/examples/neshan-mapbox-draw-route/
 * @param {object} routeGeometry - routes[0] از پاسخ API نشان
 * @returns {Array<[number,number]>} آرایهٔ [lat, lng] برای L.polyline؛ در صورت خطا null
 */
function decodeRouteGeometry(routeGeometry) {
  if (!routeGeometry || typeof polyline === 'undefined' || typeof polyline.decode !== 'function') return null;
  const precision = 5;
  const points = [];
  try {
    const overviewEncoded = (routeGeometry.overview_polyline && routeGeometry.overview_polyline.points) || (typeof routeGeometry.overview_polyline === 'string' ? routeGeometry.overview_polyline : null);
    if (overviewEncoded && typeof overviewEncoded === 'string') {
      const decoded = polyline.decode(overviewEncoded, precision);
      decoded.forEach((p) => points.push([p[0], p[1]]));
    }
    if (points.length === 0 && routeGeometry.legs && Array.isArray(routeGeometry.legs)) {
      for (const leg of routeGeometry.legs) {
        const steps = leg.steps || [];
        for (const step of steps) {
          const encoded = step.polyline;
          if (encoded && typeof encoded === 'string') {
            const decoded = polyline.decode(encoded, precision);
            decoded.forEach((p) => points.push([p[0], p[1]]));
          }
        }
      }
    }
    return points.length > 0 ? points : null;
  } catch (e) {
    return null;
  }
}

function drawStraightRouteLine(map, startLat, startLng, destLat, destLng, routeGeometry) {
  if (!map || typeof L === 'undefined') return;
  let linePoints = null;
  if (routeGeometry) linePoints = decodeRouteGeometry(routeGeometry);
  if (!linePoints || linePoints.length === 0) linePoints = [[startLat, startLng], [destLat, destLng]];
  if (window.currentPath && map) map.removeLayer(window.currentPath);
  if (window.routeLayer && map) map.removeLayer(window.routeLayer);
  if (window.currentRoute && map) map.removeLayer(window.currentRoute);
  if (window.team13RouteLine && map) map.removeLayer(window.team13RouteLine);
  const routePane = map.getPane && map.getPane('team13-route-pane') ? 'team13-route-pane' : 'overlayPane';
  window.currentPath = L.polyline(linePoints, {
    color: '#40916c',
    weight: 6,
    opacity: 1,
    pane: routePane,
  }).addTo(map);
  if (window.currentPath.bringToFront) window.currentPath.bringToFront();
  window.routeLayer = window.currentPath;
  window.currentRoute = window.currentPath;
  window.team13RouteLine = window.currentPath;
  map.fitBounds(window.currentPath.getBounds(), { padding: [40, 40] });
}

/**
 * مسیر از موقعیت کاربر تا نقطهٔ مقصد — ETA از بک‌اند، رسم خط مستقیم.
 * @param {object} [options] - اختیاری: { no_traffic: true, bearing: 0-360 } برای سرویس بدون ترافیک نشان
 */
async function getRouteFromUserToPoint(destinationCoords, serviceType, options) {
  const map = window.team13MapInstance;
  if (!map || typeof L === 'undefined') throw new Error('Map not ready');

  const destLat = destinationCoords && typeof destinationCoords.lat === 'number' ? destinationCoords.lat : parseFloat(destinationCoords?.lat);
  const destLng = destinationCoords && typeof destinationCoords.lng === 'number' ? destinationCoords.lng : parseFloat(destinationCoords?.lng);
  if (isNaN(destLat) || isNaN(destLng)) throw new Error('Invalid destination coordinates');

  const position = await new Promise((resolve, reject) => {
    if (!navigator.geolocation) return reject(new Error('Geolocation not supported'));
    navigator.geolocation.getCurrentPosition(resolve, (e) => reject(new Error(e.message || 'موقعیت یافت نشد')), { enableHighAccuracy: true, timeout: 10000, maximumAge: 60000 });
  });
  const startLat = position.coords.latitude;
  const startLng = position.coords.longitude;
  const travelMode = toTravelMode(serviceType);
  const routeParams = {
    source_lat: String(startLat),
    source_lng: String(startLng),
    source_name: 'موقعیت من',
    dest_lat: String(destLat),
    dest_lng: String(destLng),
    dest_name: 'مقصد',
    travel_mode: travelMode,
  };
  if (options && options.no_traffic && travelMode === 'car') routeParams.no_traffic = '1';
  if (options && options.bearing != null && options.bearing >= 0 && options.bearing <= 360) routeParams.bearing = String(options.bearing);

  const data = await fetchData('routes/', routeParams);
  drawStraightRouteLine(map, startLat, startLng, destLat, destLng, data.route_geometry || null);
  const distanceKm = data.distance_km != null ? Number(data.distance_km) : null;
  let durationMinutes = data.eta_minutes != null ? Number(data.eta_minutes) : null;
  const type = (travelMode === 'walk' ? 'walking' : travelMode === 'bicycle' ? 'bicycle' : travelMode === 'transit' ? 'transit' : 'driving');
  if (durationMinutes != null && travelMode === 'bicycle') durationMinutes = Math.round(durationMinutes * 1.55);
  if (durationMinutes != null && (travelMode === 'walk' || travelMode === 'walking')) durationMinutes = Math.round(durationMinutes * 3);
  return { distanceKm, durationMinutes, serviceType: type, eta_source: data.eta_source };
}

/**
 * مسیر بین دو نقطه — ETA از بک‌اند، رسم خط مستقیم.
 * @param {object} [options] - اختیاری: { no_traffic: true, bearing: 0-360 } برای سرویس بدون ترافیک نشان
 */
async function getRouteFromTo(startCoords, destCoords, serviceType, options) {
  const map = window.team13MapInstance;
  if (!map || typeof L === 'undefined') throw new Error('Map not ready');

  const startLat = startCoords && typeof startCoords.lat === 'number' ? startCoords.lat : parseFloat(startCoords?.lat);
  const startLng = startCoords && typeof startCoords.lng === 'number' ? startCoords.lng : parseFloat(startCoords?.lng);
  const destLat = destCoords && typeof destCoords.lat === 'number' ? destCoords.lat : parseFloat(destCoords?.lat);
  const destLng = destCoords && typeof destCoords.lng === 'number' ? destCoords.lng : parseFloat(destCoords?.lng);
  if (isNaN(startLat) || isNaN(startLng) || isNaN(destLat) || isNaN(destLng)) throw new Error('Invalid start or destination coordinates');

  const travelMode = toTravelMode(serviceType);
  const routeParams = {
    source_lat: String(startLat),
    source_lng: String(startLng),
    source_name: 'مبدأ',
    dest_lat: String(destLat),
    dest_lng: String(destLng),
    dest_name: 'مقصد',
    travel_mode: travelMode,
  };
  if (options && options.no_traffic && travelMode === 'car') routeParams.no_traffic = '1';
  if (options && options.bearing != null && options.bearing >= 0 && options.bearing <= 360) routeParams.bearing = String(options.bearing);

  const data = await fetchData('routes/', routeParams);
  drawStraightRouteLine(map, startLat, startLng, destLat, destLng, data.route_geometry || null);
  const distanceKm = data.distance_km != null ? Number(data.distance_km) : null;
  let durationMinutes = data.eta_minutes != null ? Number(data.eta_minutes) : null;
  const type = (travelMode === 'walk' ? 'walking' : travelMode === 'bicycle' ? 'bicycle' : travelMode === 'transit' ? 'transit' : 'driving');
  if (durationMinutes != null && travelMode === 'bicycle') durationMinutes = Math.round(durationMinutes * 4.55);
  if (durationMinutes != null && (travelMode === 'walk' || travelMode === 'walking')) durationMinutes = Math.round(durationMinutes * 3);
  return { distanceKm, durationMinutes, serviceType: type, eta_source: data.eta_source };
}

/**
 * تبدیل مختصات به آدرس (Reverse Geocoding) نشان.
 * خروجی: { status, formatted_address, address, address_compact, route_name, route_type,
 *   neighbourhood, city, state, place, municipality_zone, in_traffic_zone, in_odd_even_zone,
 *   village, county, district } یا null.
 */
async function reverseGeocode(lat, lon) {
  if (lat == null || lon == null || isNaN(Number(lat)) || isNaN(Number(lon))) return null;
  try {
    const data = await fetchData('reverse-geocode/', { lat: String(lat), lng: String(lon) });
    return data;
  } catch {
    return null;
  }
}

/**
 * تبدیل آدرس متنی به مختصات (Geocoding) نشان.
 * @param {string} address - آدرس مورد نظر
 * @param {{ province?: string, city?: string, lat?: number, lng?: number, plus?: boolean, extent?: object }} [options]
 * @returns {Promise<{ items: Array<{ location: { latitude, longitude }, province, city, neighbourhood, unMatchedTerm }> }>}
 */
async function geocode(address, options = {}) {
  if (!address || String(address).trim() === '') return { items: [] };
  try {
    return await api.geocode(address, options);
  } catch {
    return { items: [] };
  }
}

async function getCityFromCoords(lat, lng) {
  return null;
}

async function findNearest(category) {
  return null;
}

/**
 * بهینه‌سازی ترتیب بازدید از چند نقطه (TSP).
 * waypoints: آرایهٔ [ [lat,lng], ... ] یا رشتهٔ "lat,lng|lat,lng|..."
 * خروجی: { points: [ { name, location: [lng,lat], index }, ... ] } به ترتیب بهینه.
 */
async function getTspOrder(waypoints, options = {}) {
  const data = await api.tsp(waypoints, options);
  return data;
}

/**
 * رسم ترتیب بهینهٔ TSP روی نقشه (خط اتصال نقاط به ترتیب).
 * points: آرایهٔ خروجی TSP؛ هر نقطه location: [lng, lat].
 */
function drawTspOrderOnMap(map, points, lineOptions) {
  if (!map || typeof L === 'undefined' || !points || points.length < 2) return null;
  const latlngs = points.map(p => {
    const loc = p.location;
    return [loc[1], loc[0]];
  });
  if (window.team13TspLine && map) map.removeLayer(window.team13TspLine);
  window.team13TspLine = L.polyline(latlngs, {
    color: (lineOptions && lineOptions.color) || '#e07c24',
    weight: (lineOptions && lineOptions.weight) || 5,
    opacity: 0.9,
    dashArray: '8,8',
    ...lineOptions,
  }).addTo(map);
  map.fitBounds(window.team13TspLine.getBounds(), { padding: [40, 40] });
  return window.team13TspLine;
}

/**
 * دریافت محدوده در دسترس (Isochrone) از بک‌اند.
 * حداقل یکی از options.distance_km یا options.time_minutes الزامی است.
 */
async function getIsochrone(lat, lng, options) {
  return api.isochrone(lat, lng, options);
}

/**
 * رسم GeoJSON محدوده در دسترس (Isochrone) روی نقشه.
 * geojson: پاسخ سرویس (FeatureCollection با geometry نوع Polygon یا LineString).
 */
function drawIsochroneOnMap(map, geojson, layerOptions) {
  if (!map || typeof L === 'undefined' || !geojson || !geojson.features) return null;
  if (window.team13IsochroneLayer && map) map.removeLayer(window.team13IsochroneLayer);
  const style = {
    color: (layerOptions && layerOptions.color) || '#2563eb',
    weight: (layerOptions && layerOptions.weight) || 2,
    opacity: 0.8,
    fillColor: (layerOptions && layerOptions.fillColor) || '#3b82f6',
    fillOpacity: (layerOptions && layerOptions.fillOpacity) != null ? layerOptions.fillOpacity : 0.15,
    ...layerOptions,
  };
  window.team13IsochroneLayer = L.geoJSON(geojson, { style }).addTo(map);
  if (window.team13IsochroneLayer.getBounds && window.team13IsochroneLayer.getBounds().isValid()) {
    map.fitBounds(window.team13IsochroneLayer.getBounds(), { padding: [40, 40] });
  }
  return window.team13IsochroneLayer;
}

/**
 * نگاشت نقاط خام (مثلاً GPS) به مسیر روی نقشه (Map Matching).
 * path: رشتهٔ lat,lng|lat,lng|... یا آرایهٔ [[lat,lng], ...].
 */
async function getMapMatching(path) {
  return api.mapMatching(path);
}

/**
 * رسم مسیر نگاشت‌شده (Map Matching) روی نقشه.
 * data: پاسخ سرویس { snappedPoints, geometry }؛ geometry = Encoded Polyline.
 */
function drawMapMatchedRouteOnMap(map, data, lineOptions) {
  if (!map || typeof L === 'undefined' || !data) return null;
  let latlngs = null;
  if (data.geometry && typeof decodeRouteGeometry === 'function') {
    latlngs = decodeRouteGeometry({ overview_polyline: { points: data.geometry } });
  }
  if ((!latlngs || latlngs.length < 2) && data.snappedPoints && data.snappedPoints.length >= 2) {
    latlngs = data.snappedPoints.map(p => {
      const loc = p.location;
      return Array.isArray(loc) ? [loc[0], loc[1]] : [loc.lat, loc.lng];
    });
  }
  if (!latlngs || latlngs.length < 2) return null;
  if (window.team13MapMatchingLine && map) map.removeLayer(window.team13MapMatchingLine);
  window.team13MapMatchingLine = L.polyline(latlngs, {
    color: (lineOptions && lineOptions.color) || '#059669',
    weight: (lineOptions && lineOptions.weight) || 5,
    opacity: 0.9,
    ...lineOptions,
  }).addTo(map);
  map.fitBounds(window.team13MapMatchingLine.getBounds(), { padding: [40, 40] });
  return window.team13MapMatchingLine;
}

if (typeof window !== 'undefined') {
  window.Team13Api = {
    fetchData,
    getCsrfToken,
    postRating,
    postJson,
    api,
    loadMapData,
    loadMoreMapPlaces: typeof loadMoreMapPlaces !== 'undefined' ? loadMoreMapPlaces : undefined,
    emergency: (api && api.emergency) ? api.emergency.bind(api) : undefined,
    getRouteFromUserToPoint,
    getRouteFromTo,
    getMapirRoute: getRouteFromUserToPoint,
    getMapirRouteFromTo: getRouteFromTo,
    getTspOrder,
    drawTspOrderOnMap,
    getIsochrone,
    drawIsochroneOnMap,
    getMapMatching,
    drawMapMatchedRouteOnMap,
    findNearest,
    reverseGeocode,
    geocode,
    getCityFromCoords,
    decodeRouteGeometry,
  };
}
