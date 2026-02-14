/**
 * Team 13 — همگام‌سازی لایه‌ها، جستجو، مسیریابی و ETA از بک‌اند، مراکز امدادی.
 * جستجوی آدرس با API جدید بعداً اضافه می‌شود.
 */
(function () {
  var SAGE_GREEN = '#40916c';
  var EVENT_MARKER_COLOR = '#c1121f';

  var MAP_DATA_CACHE_KEY = 'team13_map_data_cache';
  var MAX_CACHED_PLACES = 2000;
  var MAX_CACHED_EVENTS = 500;

  function loadMapDataCache() {
    try {
      var raw = typeof localStorage !== 'undefined' && localStorage.getItem(MAP_DATA_CACHE_KEY);
      if (!raw) return null;
      var data = JSON.parse(raw);
      if (!data || !Array.isArray(data.places) || !Array.isArray(data.events)) return null;
      return {
        places: data.places,
        events: data.events,
        placesNextPage: typeof data.placesNextPage === 'number' ? data.placesNextPage : 1
      };
    } catch (e) { /* ignore */ }
    return null;
  }

  function saveMapDataCache() {
    try {
      if (typeof localStorage === 'undefined') return;
      var places = window._team13PlacesCache || [];
      var events = window._team13EventsCache || [];
      var nextPage = window._team13PlacesNextPage;
      if (places.length === 0 && events.length === 0) return;
      var payload = {
        places: places.slice(0, MAX_CACHED_PLACES),
        events: events.slice(0, MAX_CACHED_EVENTS),
        placesNextPage: typeof nextPage === 'number' ? nextPage : 1,
        savedAt: Date.now()
      };
      localStorage.setItem(MAP_DATA_CACHE_KEY, JSON.stringify(payload));
    } catch (e) { /* ignore */ }
  }

  if (typeof window !== 'undefined') {
    window.allMarkers = window.allMarkers || {};
    window.currentlyShownPoiMarker = window.currentlyShownPoiMarker || null;
    window.emergencyPoiMarker = window.emergencyPoiMarker || null;
    window._team13PoiIconsVisible = window._team13PoiIconsVisible !== false;
    window._team13PoiFilter = window._team13PoiFilter || 'all'; /* 'all' | 'places' | 'events' | 'none' */
    window._team13PlacesTypeFilter = window._team13PlacesTypeFilter || null; /* null = all types, or string[] e.g. ['food','hotel'] */
    window.isPlacementMode = false;
    var cachedMap = loadMapDataCache();
    if (cachedMap && (cachedMap.places.length > 0 || cachedMap.events.length > 0)) {
      window._team13PlacesCache = cachedMap.places;
      window._team13EventsCache = cachedMap.events;
      window._team13PlacesNextPage = cachedMap.placesNextPage;
    }
  }

  function getMap() {
    return window.team13MapInstance || null;
  }

  function getConfig() {
    return window.MAPIR_CONFIG || {};
  }

  function escapeHtml(s) {
    if (!s) return '';
    var div = document.createElement('div');
    div.textContent = s;
    return div.innerHTML;
  }

  // --- Category-specific POI icon config: emoji + color (pin style) ---
  var POI_ICON_MAP = {
    food: { emoji: '🍴', color: '#f97316', label: 'رستوران' },
    restaurant: { emoji: '🍴', color: '#f97316', label: 'رستوران' },
    hotel: { emoji: '🏨', color: '#2563eb', label: 'هتل' },
    hospital: { emoji: '🏥', color: '#dc2626', label: 'بیمارستان' },
    fire_station: { emoji: '🚒', color: '#ea580c', label: 'آتش‌نشانی' },
    pharmacy: { emoji: '💊', color: '#7c3aed', label: 'داروخانه' },
    clinic: { emoji: '🩺', color: '#0d9488', label: 'کلینیک' },
    museum: { emoji: '🏛️', color: '#92400e', label: 'موزه' },
    entertainment: { emoji: '🎡', color: '#16a34a', label: 'تفریحی' },
    gym: { emoji: '🏋️', color: '#059669', label: 'ورزشگاه' },
    other: { emoji: '📍', color: SAGE_GREEN, label: 'سایر' },
  };

  /** ترتیب و کلیدهای نوع مکان برای فیلتر (بدون تکرار restaurant؛ با food نمایش داده می‌شود) */
  var PLACE_TYPES_FOR_FILTER = [
    { key: 'food', label: 'رستوران' },
    { key: 'hotel', label: 'هتل' },
    { key: 'hospital', label: 'بیمارستان' },
    { key: 'fire_station', label: 'آتش‌نشانی' },
    { key: 'pharmacy', label: 'داروخانه' },
    { key: 'clinic', label: 'کلینیک' },
    { key: 'museum', label: 'موزه' },
    { key: 'entertainment', label: 'تفریحی' },
    { key: 'gym', label: 'ورزشگاه' },
    { key: 'other', label: 'سایر' },
  ];

  function getPoiIconConfig(type) {
    var t = (type || '').toLowerCase().trim();
    return POI_ICON_MAP[t] || POI_ICON_MAP.other;
  }

  function createPlaceIcon(type) {
    if (typeof L === 'undefined') return null;
    var cfg = getPoiIconConfig(type);
    var html = '<span class="team13-poi-pin" style="' +
      'width:32px;height:32px;background:' + cfg.color + ';' +
      'border:2px solid #fff;border-radius:50%;' +
      'box-shadow:0 3px 10px rgba(0,0,0,0.25);' +
      'display:flex;align-items:center;justify-content:center;' +
      'font-size:16px;line-height:1;">' + cfg.emoji + '</span>';
    return L.divIcon({
      className: 'team13-place-marker team13-poi-marker',
      html: html,
      iconSize: [32, 32],
      iconAnchor: [16, 16],
    });
  }

  function createDiscoveryPlaceIcon(type) {
    if (typeof L === 'undefined') return null;
    var cfg = getPoiIconConfig(type);
    var html = '<span class="team13-poi-pin team13-discovery-marker" style="' +
      'width:32px;height:32px;background:' + cfg.color + ';' +
      'border:2px solid #fff;border-radius:50%;' +
      'box-shadow:0 3px 10px rgba(0,0,0,0.25);' +
      'display:flex;align-items:center;justify-content:center;' +
      'font-size:16px;line-height:1;">' + cfg.emoji + '</span>';
    return L.divIcon({
      className: 'team13-place-marker team13-discovery-marker',
      html: html,
      iconSize: [32, 32],
      iconAnchor: [16, 16],
    });
  }

  function createDiscoveryUserContributedIcon() {
    if (typeof L === 'undefined') return null;
    var html = '<span class="team13-poi-pin team13-discovery-marker team13-user-contributed-pin" style="' +
      'width:32px;height:32px;background:#f59e0b;border:2px solid #fbbf24;border-radius:50%;' +
      'box-shadow:0 3px 10px rgba(0,0,0,0.25);display:flex;align-items:center;justify-content:center;font-size:16px;">⭐</span>';
    return L.divIcon({
      className: 'team13-place-marker team13-discovery-marker team13-user-contributed-marker',
      html: html,
      iconSize: [32, 32],
      iconAnchor: [16, 16],
    });
  }

  function createEventIcon() {
    if (typeof L === 'undefined') return null;
    return L.divIcon({
      className: 'team13-event-marker',
      html: '<span style="width:22px;height:22px;background:' + EVENT_MARKER_COLOR + ';border:2px solid #9d0208;border-radius:4px;display:block;box-shadow:0 2px 4px rgba(0,0,0,0.2);"></span>',
      iconSize: [22, 22],
      iconAnchor: [11, 11],
    });
  }

  function createSearchResultIcon() {
    if (typeof L === 'undefined') return null;
    return L.divIcon({
      className: 'team13-search-marker',
      html: '<span style="width:20px;height:20px;background:#2563eb;border:2px solid #1d4ed8;border-radius:50%;display:block;box-shadow:0 2px 6px rgba(0,0,0,0.3);"></span>',
      iconSize: [20, 20],
      iconAnchor: [10, 10],
    });
  }

  function createSelectedPlaceIcon() {
    if (typeof L === 'undefined') return null;
    return L.divIcon({
      className: 'team13-place-marker team13-marker-selected',
      html: '<span style="width:24px;height:24px;background:' + SAGE_GREEN + ';border:2px solid #1b4332;border-radius:50%;display:block;box-shadow:0 2px 8px rgba(64,145,108,0.5);"></span>',
      iconSize: [24, 24],
      iconAnchor: [12, 12],
    });
  }

  function createSelectedEventIcon() {
    if (typeof L === 'undefined') return null;
    return L.divIcon({
      className: 'team13-event-marker team13-marker-selected',
      html: '<span style="width:22px;height:22px;background:' + SAGE_GREEN + ';border:2px solid #1b4332;border-radius:4px;display:block;box-shadow:0 2px 8px rgba(64,145,108,0.5);"></span>',
      iconSize: [22, 22],
      iconAnchor: [11, 11],
    });
  }

  function createEmergencyPoiIcon() {
    if (typeof L === 'undefined') return null;
    return L.divIcon({
      className: 'team13-emergency-poi-marker team13-marker-selected',
      html: '<span style="width:26px;height:26px;background:' + SAGE_GREEN + ';border:2px solid #1b4332;border-radius:50%;display:block;box-shadow:0 2px 10px rgba(64,145,108,0.6);"></span>',
      iconSize: [26, 26],
      iconAnchor: [13, 13],
    });
  }

  function createStartMarkerIcon() {
    if (typeof L === 'undefined') return null;
    return L.divIcon({
      className: 'team13-route-start-marker',
      html: '<span style="width:28px;height:28px;background:#22c55e;border:2px solid #1b4332;border-radius:50%;display:block;box-shadow:0 2px 8px rgba(0,0,0,0.25);font-size:12px;line-height:24px;text-align:center;color:#fff;font-weight:bold;">A</span>',
      iconSize: [28, 28],
      iconAnchor: [14, 14],
    });
  }

  function createDestMarkerIcon() {
    if (typeof L === 'undefined') return null;
    return L.divIcon({
      className: 'team13-route-dest-marker',
      html: '<span style="width:28px;height:28px;background:#dc2626;border:2px solid #991b1b;border-radius:50%;display:block;box-shadow:0 2px 8px rgba(0,0,0,0.25);font-size:12px;line-height:24px;text-align:center;color:#fff;font-weight:bold;">B</span>',
      iconSize: [28, 28],
      iconAnchor: [14, 14],
    });
  }

  /** Live user location: blue pulse marker (silent, no popup). */
  function createUserLocationIcon() {
    if (typeof L === 'undefined') return null;
    return L.divIcon({
      className: 'team13-user-location-marker',
      html: '<span class="team13-user-location-pulse"></span><span class="team13-user-location-dot"></span>',
      iconSize: [32, 32],
      iconAnchor: [16, 16],
    });
  }

  // --- Popup: Place — همان قالب پاپ‌آپ «انتخاب نقطه» برای یکپارچگی UI ---
  function buildPlacePopupContent(p, lat, lng) {
    var name = (p.name_fa || p.name_en || p.type_display || '').trim() || p.place_id;
    var typeDisplay = (p.type_display || p.type || '').trim() || '—';
    var address = (p.address || p.city || '').trim() || '—';
    var placeId = (p.place_id || p.id || '').toString();
    var base = (window.TEAM13_API_BASE || '/team13').replace(/\/$/, '');
    var detailPageUrl = base + '/places/' + (placeId || '') + '/';
    var rating = p.rating != null && !isNaN(parseFloat(p.rating)) ? parseFloat(p.rating) : null;
    var ratingHtml = rating != null ? ' · امتیاز: ' + rating + '/۵' : '';
    var addressLine = escapeHtml(name) + (typeDisplay !== '—' ? ' · ' + escapeHtml(typeDisplay) : '') + ratingHtml + (address !== '—' ? '<br><span class="text-muted">' + escapeHtml(address) + '</span>' : '');
    var btnDetails = '<button type="button" class="team13-reverse-popup-btn team13-btn-place-details" data-place-id="' + escapeHtml(placeId) + '" data-lat="' + lat + '" data-lng="' + lng + '" data-name="' + escapeHtml(name) + '">جزئیات (امتیاز / نظر / عکس)</button>';
    var linkDetailPage = '<a href="' + escapeHtml(detailPageUrl) + '" class="team13-reverse-popup-btn team13-btn-place-detail-page">صفحهٔ جزئیات مکان</a>';
    var btnRoute = '<button type="button" class="team13-reverse-popup-btn team13-btn-route-to-place" data-lat="' + lat + '" data-lng="' + lng + '" data-name="' + escapeHtml(name) + '">مسیریابی به اینجا</button>';
    return '<div class="team13-reverse-popup-content" dir="rtl">' +
      '<p class="team13-reverse-popup-address">' + addressLine + '</p>' +
      '<div class="team13-reverse-popup-actions">' + btnDetails + ' ' + linkDetailPage + ' ' + btnRoute + '</div>' +
      '</div>';
  }

  // --- Popup: Event — همان قالب پاپ‌آپ «انتخاب نقطه» برای یکپارچگی UI ---
  function buildEventPopupContent(e) {
    var lat = parseFloat(e.latitude);
    var lng = parseFloat(e.longitude);
    var title = (e.title_fa || e.title_en || e.event_id || '').trim();
    var timeText = (e.start_at || e.start_at_iso || '') + (e.end_at || e.end_at_iso ? ' تا ' + (e.end_at || e.end_at_iso) : '');
    var addressLine = escapeHtml(title) + '<br><span class="text-muted">زمان: ' + escapeHtml(timeText || '—') + '</span>';
    var routeBtn = '<button type="button" class="team13-reverse-popup-btn team13-btn-route-to-event" data-lat="' + lat + '" data-lng="' + lng + '" data-name="' + escapeHtml(title) + '">مسیریابی به رویداد</button>';
    return '<div class="team13-reverse-popup-content" dir="rtl">' +
      '<p class="team13-reverse-popup-address">' + addressLine + '</p>' +
      '<div class="team13-reverse-popup-actions">' + routeBtn + '</div>' +
      '</div>';
  }

  // --- Sync DB layers: fetch places + events from our API, add markers, sidebar cards ---
  function syncDatabaseLayers() {
    var map = getMap();
    if (!map || !window.Team13Api || !window.Team13Api.loadMapData) return Promise.reject(new Error('Map or API not ready'));

    return window.Team13Api.loadMapData().then(function (data) {
      var places = data.places || [];
      var events = data.events || [];
      window._team13PlacesCache = places;
      window._team13EventsCache = events;
      clearPlaceAndEventMarkers(map);
      window.allMarkers = {};
      addPlaceMarkers(map, places);
      addEventMarkers(map, events);
      injectSidebarCards(places, events);
      bindRouteButtonInPopups(map);
      setPoiIconsVisible(window._team13PoiIconsVisible);
      saveMapDataCache();
      var count = (places.length || 0) + (events.length || 0);
      if (count > 0 && window._team13PoiIconsVisible) {
        setTimeout(function () { setPoiIconsVisible(true); }, 250);
      }
      if (!window._team13LoadMoreTimerStarted && window.Team13Api && typeof window.Team13Api.loadMoreMapPlaces === 'function') {
        window._team13LoadMoreTimerStarted = true;
        setInterval(function () {
          var m = getMap();
          if (!m) return;
          window.Team13Api.loadMoreMapPlaces().then(function (result) {
            if (result.added > 0 && result.places && result.places.length) {
              clearPlaceMarkersOnly(m);
              addPlaceMarkers(m, result.places);
              saveMapDataCache();
              if (window.showToast) window.showToast('نمایش ' + result.places.length + ' مکان روی نقشه');
            }
          }).catch(function () {});
        }, 45000);
      }
      return { places: places, events: events };
    });
  }

  function clearPlaceAndEventMarkers(map) {
    if (!map) return;
    var allMarkers = window.allMarkers || {};
    Object.keys(allMarkers).forEach(function (id) {
      var m = allMarkers[id];
      if (m && typeof m.remove === 'function') m.remove();
    });
    window.allMarkers = {};
    if (window.currentlyShownPoiMarker) {
      map.removeLayer(window.currentlyShownPoiMarker);
      window.currentlyShownPoiMarker = null;
    }
    if (window.team13PlaceLayerGroup) {
      map.removeLayer(window.team13PlaceLayerGroup);
      window.team13PlaceLayerGroup.clearLayers && window.team13PlaceLayerGroup.clearLayers();
      window.team13PlaceLayerGroup = null;
    }
    if (window.team13EventLayerGroup) {
      map.removeLayer(window.team13EventLayerGroup);
      window.team13EventLayerGroup.clearLayers && window.team13EventLayerGroup.clearLayers();
      window.team13EventLayerGroup = null;
    }
    if (window.team13CityEventLayerGroup) {
      map.removeLayer(window.team13CityEventLayerGroup);
      window.team13CityEventLayerGroup = null;
    }
  }

  /** فقط لایهٔ مکان‌ها را پاک می‌کند (برای به‌روزرسانی پس از بار بیشتر). */
  function clearPlaceMarkersOnly(map) {
    if (!map) return;
    var allMarkers = window.allMarkers || {};
    Object.keys(allMarkers).forEach(function (id) {
      if (id.indexOf('place-') !== 0) return;
      var m = allMarkers[id];
      if (m && typeof m.remove === 'function') m.remove();
      delete allMarkers[id];
    });
    window.allMarkers = allMarkers;
    if (window.team13PlaceLayerGroup) {
      map.removeLayer(window.team13PlaceLayerGroup);
      window.team13PlaceLayerGroup.clearLayers && window.team13PlaceLayerGroup.clearLayers();
      window.team13PlaceLayerGroup = null;
    }
  }

  /**
   * Apply city-based event filter: clear event markers on map, filter by city, render filtered markers, update sidebar, optional center.
   * @param {string|null} cityName - null = show all events in sidebar only (no event markers on map)
   * @param {number|null} centerLat - optional center for map
   * @param {number|null} centerLng - optional center for map
   */
  function applyEventCityFilter(cityName, centerLat, centerLng) {
    var map = getMap();
    var events = window._team13EventsCache || [];
    if (!map || !L) return;

    var filtered = events;
    if (cityName && String(cityName).trim()) {
      var cityNorm = String(cityName).trim();
      filtered = events.filter(function (e) {
        var c = (e.city && String(e.city).trim()) || '';
        return c === cityNorm;
      });
    }

    if (window.team13CityEventLayerGroup) {
      map.removeLayer(window.team13CityEventLayerGroup);
      window.team13CityEventLayerGroup = null;
    }

    injectEventsList(filtered);

    if (!cityName || !String(cityName).trim()) {
      window.allMarkers = {};
      addPlaceMarkers(map, window._team13PlacesCache || []);
      addEventMarkers(map, window._team13EventsCache || []);
    } else if (filtered.length > 0) {
      var layer = L.layerGroup();
      var icon = createEventIcon();
      var allMarkers = Object.assign({}, window.allMarkers || {});
      filtered.forEach(function (e) {
        var lat = parseFloat(e.latitude);
        var lng = parseFloat(e.longitude);
        if (isNaN(lat) || isNaN(lng)) return;
        var id = 'event-' + (e.event_id || e.id || String(lat) + ',' + String(lng));
        var popupContent = buildEventPopupContent(e);
        var m = L.marker([lat, lng], { icon: icon }).bindPopup(popupContent);
        layer.addLayer(m);
        allMarkers[id] = m;
        if (window._team13PoiIconsVisible && typeof m.addTo === 'function') m.addTo(map);
      });
      window.allMarkers = allMarkers;
      if (window._team13PoiIconsVisible) layer.addTo(map);
      window.team13CityEventLayerGroup = layer;
      if (centerLat != null && centerLng != null && !isNaN(centerLat) && !isNaN(centerLng)) {
        flyTo(map, centerLat, centerLng, 12);
      } else {
        var first = filtered[0];
        flyTo(map, parseFloat(first.latitude), parseFloat(first.longitude), 11);
      }
    } else if (centerLat != null && centerLng != null && !isNaN(centerLat) && !isNaN(centerLng)) {
      flyTo(map, centerLat, centerLng, 12);
    }
  }

  /** Update only the events list in sidebar (used by city filter). */
  function injectEventsList(events) {
    var eventsList = document.getElementById('events-list');
    if (!eventsList) return;
    eventsList.innerHTML = '';
    (events || []).forEach(function (e) {
      eventsList.insertAdjacentHTML('beforeend', renderEventCard(e));
    });
  }

  /** لایهٔ واحد مکان‌ها روی نقشه تا آیکون‌ها حتماً نمایش داده شوند. */
  function getOrCreatePlaceLayerGroup(map) {
    if (!map || !L) return null;
    if (window.team13PlaceLayerGroup) return window.team13PlaceLayerGroup;
    window.team13PlaceLayerGroup = L.layerGroup();
    return window.team13PlaceLayerGroup;
  }

  /** لایهٔ واحد رویدادها روی نقشه. */
  function getOrCreateEventLayerGroup(map) {
    if (!map || !L) return null;
    if (window.team13EventLayerGroup) return window.team13EventLayerGroup;
    window.team13EventLayerGroup = L.layerGroup();
    return window.team13EventLayerGroup;
  }

  /** مکان‌های دیتابیس را روی نقشه نمایش می‌دهد. نقشهٔ نشان (Mapbox) لایهٔ گروه را روی نقشه اضافه نمی‌کند؛ هر مارکر باید خودش addTo(map) شود. */
  function addPlaceMarkers(map, places) {
    if (!map || !L) return;
    var layerGroup = getOrCreatePlaceLayerGroup(map);
    if (!layerGroup) return;
    var allMarkers = Object.assign({}, window.allMarkers || {});
    (places || []).forEach(function (p) {
      var lat = parseFloat(p.latitude);
      var lng = parseFloat(p.longitude);
      if (isNaN(lat) || isNaN(lng)) return;
      var id = 'place-' + (p.place_id || p.id || String(lat) + ',' + String(lng));
      var popupContent = buildPlacePopupContent(p, lat, lng);
      var icon = (p.is_user_contributed) ? createUserContributedPlaceIcon() : createPlaceIcon(p.type || p.category);
      var m = L.marker([lat, lng], { icon: icon }).bindPopup(popupContent);
      var typeKey = ((p.type || p.category || '') + '').toLowerCase().trim() || 'other';
      if (typeKey === 'restaurant') typeKey = 'food';
      m._placeType = typeKey;
      allMarkers[id] = m;
      layerGroup.addLayer(m);
      if (window._team13PoiIconsVisible && typeof m.addTo === 'function') m.addTo(map);
    });
    window.allMarkers = allMarkers;
  }

  /** رویدادهای دیتابیس را روی نقشه نمایش می‌دهد. هر مارکر باید addTo(map) شود. */
  function addEventMarkers(map, events) {
    if (!map || !L) return;
    var layerGroup = getOrCreateEventLayerGroup(map);
    if (!layerGroup) return;
    var icon = createEventIcon();
    var allMarkers = Object.assign({}, window.allMarkers || {});
    (events || []).forEach(function (e) {
      var lat = parseFloat(e.latitude);
      var lng = parseFloat(e.longitude);
      if (isNaN(lat) || isNaN(lng)) return;
      var id = 'event-' + (e.event_id || e.id || String(lat) + ',' + String(lng));
      var popupContent = buildEventPopupContent(e);
      var m = L.marker([lat, lng], { icon: icon }).bindPopup(popupContent);
      allMarkers[id] = m;
      layerGroup.addLayer(m);
      if (window._team13PoiIconsVisible && typeof m.addTo === 'function') m.addTo(map);
    });
    window.allMarkers = allMarkers;
  }

  function clearTemporaryMapItems(map) {
    if (!map) return;
    if (window.currentlyShownPoiMarker) {
      map.removeLayer(window.currentlyShownPoiMarker);
      window.currentlyShownPoiMarker = null;
    }
    if (searchResultMarker && map.hasLayer(searchResultMarker)) {
      map.removeLayer(searchResultMarker);
      searchResultMarker = null;
    }
    if (favoritePickMarker && map.hasLayer(favoritePickMarker)) {
      map.removeLayer(favoritePickMarker);
      favoritePickMarker = null;
    }
    if (window.emergencyPoiMarker && map.hasLayer(window.emergencyPoiMarker)) {
      map.removeLayer(window.emergencyPoiMarker);
      window.emergencyPoiMarker = null;
    }
    var routeLayer = window.currentPath || window.routeLayer || window.currentRoute || window.team13RouteLine;
    if (routeLayer && map.hasLayer(routeLayer)) {
      map.removeLayer(routeLayer);
    }
    window.currentPath = null;
    window.routeLayer = null;
    window.currentRoute = null;
    window.team13RouteLine = null;
  }

  function showPoiMarkerById(map, id, lat, lng, isPlace) {
    var allMarkers = window.allMarkers || {};
    var marker = allMarkers[id];
    if (!marker) return;
    clearTemporaryMapItems(map);
    marker.setIcon(isPlace ? createSelectedPlaceIcon() : createSelectedEventIcon());
    marker.addTo(map);
    window.currentlyShownPoiMarker = marker;
    flyTo(map, lat, lng, 15);
    marker.openPopup();
  }

  function runRouteToPoint(lat, lng, name) {
    if (isNaN(lat) || isNaN(lng)) return;
    setRouteLoading(true);
    if (window.Team13Api && typeof window.Team13Api.getRouteFromTo === 'function') {
      getCurrentPosition()
        .then(function (pos) {
          var userLat = pos.coords.latitude;
          var userLng = pos.coords.longitude;
          switchToRoutesTabAndSetRoute(userLat, userLng, lat, lng, name || 'مقصد', 'driving');
          setRouteLoading(false);
        })
        .catch(function () {
          setDestFromCoords(lat, lng, name || '');
          var tabBtn = document.querySelector('[data-tab="routes"]');
          if (tabBtn) tabBtn.click();
          setRouteLoading(false);
          if (window.showToast) window.showToast('مقصد تنظیم شد. مبدا را انتخاب کنید.');
        });
    } else if (window.Team13Api && typeof window.Team13Api.getRouteFromUserToPoint === 'function') {
      window.Team13Api.getRouteFromUserToPoint({ lat: lat, lng: lng }, 'driving')
        .then(function (r) {
          setRouteLoading(false);
          if (typeof window.updateRouteInfoBox === 'function') window.updateRouteInfoBox(r);
          var distStr = r && r.distanceKm != null ? (Math.round(r.distanceKm * 10) / 10) + ' کیلومتر' : '';
          var timeStr = r && r.durationMinutes != null ? r.durationMinutes + ' دقیقه' : '';
          showRouteInfo('فاصله: ' + distStr, 'زمان تقریبی: ' + timeStr);
        })
        .catch(function (err) {
          setRouteLoading(false);
          showRouteInfo('خطا: ' + (err && err.message ? err.message : 'مسیر ناموفق'), '');
        });
    } else {
      requestRouteFromUserTo(lat, lng);
    }
  }

  function bindRouteButtonInPopups(map) {
    if (!map) return;
    function bindRouteBtn(btn) {
      if (!btn) return;
      btn.onclick = function () {
        var lat = parseFloat(btn.getAttribute('data-lat'));
        var lng = parseFloat(btn.getAttribute('data-lng'));
        var name = (btn.getAttribute('data-name') || '').trim();
        runRouteToPoint(lat, lng, name);
      };
    }
    map.on('popupopen', function (e) {
      var popup = e.popup;
      var el = popup && popup.getElement && popup.getElement();
      if (!el) return;
      bindRouteBtn(el.querySelector('.team13-btn-route-to-place'));
      bindRouteBtn(el.querySelector('.team13-btn-route-to-event'));
      bindRouteBtn(el.querySelector('.team13-btn-discovery-route'));
      var btnDetails = el.querySelector('.team13-btn-place-details');
      if (btnDetails && typeof window.Team13OpenPlaceActionsModal === 'function') {
        btnDetails.onclick = function () {
          var placeId = btnDetails.getAttribute('data-place-id');
          var lat = parseFloat(btnDetails.getAttribute('data-lat'));
          var lng = parseFloat(btnDetails.getAttribute('data-lng'));
          var name = (btnDetails.getAttribute('data-name') || '').trim() || 'مکان';
          if (placeId) window.Team13OpenPlaceActionsModal(placeId, name, lat, lng);
        };
      }
    });
    if (!window._team13PopupDelegationBound) {
      window._team13PopupDelegationBound = true;
      document.addEventListener('click', function popupButtonDelegation(ev) {
        var target = ev.target;
        var routeBtn = target.closest && (target.closest('.team13-btn-route-to-place') || target.closest('.team13-btn-route-to-event') || target.closest('.team13-btn-discovery-route'));
        if (routeBtn) {
          var lat = parseFloat(routeBtn.getAttribute('data-lat'));
          var lng = parseFloat(routeBtn.getAttribute('data-lng'));
          var name = (routeBtn.getAttribute('data-name') || '').trim();
          runRouteToPoint(lat, lng, name);
          ev.preventDefault();
          ev.stopPropagation();
        }
        var detailsBtn = target.closest && target.closest('.team13-btn-place-details');
        if (detailsBtn && typeof window.Team13OpenPlaceActionsModal === 'function') {
          var placeId = detailsBtn.getAttribute('data-place-id');
          var lat = parseFloat(detailsBtn.getAttribute('data-lat'));
          var lng = parseFloat(detailsBtn.getAttribute('data-lng'));
          var name = (detailsBtn.getAttribute('data-name') || '').trim() || 'مکان';
          if (placeId) {
            window.Team13OpenPlaceActionsModal(placeId, name, lat, lng);
            ev.preventDefault();
            ev.stopPropagation();
          }
        }
      }, true);
    }
  }

  // --- User location then route + ETA ---
  function requestRouteFromUserTo(targetLat, targetLng) {
    setRouteLoading(true);
    hideRouteInfo();
    getCurrentPosition()
      .then(function (pos) {
        var userLat = pos.coords.latitude;
        var userLng = pos.coords.longitude;
        return fetchRouteAndEta(userLat, userLng, targetLat, targetLng);
      })
      .then(function (result) {
        setRouteLoading(false);
        if (result && result.polyline) {
          showRouteInfo(result.distanceText, result.etaText);
        }
      })
      .catch(function (err) {
        setRouteLoading(false);
        showRouteInfo('خطا: ' + (err && err.message ? err.message : 'موقعیت یا مسیر در دسترس نیست'), '');
      });
  }

  function getCurrentPosition() {
    return new Promise(function (resolve, reject) {
      if (!navigator.geolocation) return reject(new Error('Geolocation not supported'));
      navigator.geolocation.getCurrentPosition(
        resolve,
        function (e) {
          var msg = e.code === 1 ? 'دسترسی به موقعیت رد شد' : e.code === 2 ? 'موقعیت در دسترس نیست' : e.code === 3 ? 'زمان درخواست تمام شد' : (e.message || 'موقعیت یافت نشد');
          reject(new Error(msg));
        },
        { enableHighAccuracy: true, timeout: 20000, maximumAge: 0 }
      );
    });
  }

  function setRouteLoading(show) {
    var el = document.getElementById('team13-route-loading');
    if (el) el.hidden = !show;
  }

  function showRouteInfo(distanceText, etaText) {
    var box = document.getElementById('team13-route-info');
    var distEl = document.getElementById('team13-route-distance');
    var etaEl = document.getElementById('team13-route-eta');
    if (box) box.hidden = false;
    if (distEl) distEl.textContent = distanceText || '';
    if (etaEl) etaEl.textContent = etaText || '';
  }

  function hideRouteInfo() {
    var box = document.getElementById('team13-route-info');
    if (box) box.hidden = true;
  }

  function fetchRouteAndEta(originLat, originLng, destLat, destLng, options) {
    var map = getMap();
    if (!map || typeof L === 'undefined') return Promise.reject(new Error('Map not ready'));

    var base = (window.TEAM13_API_BASE || '/team13').replace(/\/$/, '');
    var travelMode = (options && options.travel_mode) ? String(options.travel_mode).toLowerCase() : 'car';
    if (['car', 'walk', 'transit', 'motorcycle'].indexOf(travelMode) === -1) travelMode = 'car';
    var params = new URLSearchParams({
      format: 'json',
      source_lat: String(originLat),
      source_lng: String(originLng),
      source_name: 'مبدأ',
      dest_lat: String(destLat),
      dest_lng: String(destLng),
      dest_name: 'مقصد',
      travel_mode: travelMode,
    });
    if (options && options.no_traffic && travelMode === 'car') params.set('no_traffic', '1');
    if (options && options.bearing != null && options.bearing >= 0 && options.bearing <= 360) params.set('bearing', String(options.bearing));
    var url = base + '/routes/?' + params.toString();

    return fetch(url, { method: 'GET', headers: { Accept: 'application/json' }, credentials: 'same-origin' })
      .then(function (res) { return res.json(); })
      .then(function (data) {
        var latlngs = [[originLat, originLng], [destLat, destLng]];
        if (data.route_geometry && window.Team13Api && typeof window.Team13Api.decodeRouteGeometry === 'function') {
          var decoded = window.Team13Api.decodeRouteGeometry(data.route_geometry);
          if (decoded && decoded.length > 0) latlngs = decoded;
        }
        var distanceKm = data.distance_km != null ? Number(data.distance_km) : null;
        var etaMinutes = data.eta_minutes != null ? Number(data.eta_minutes) : null;
        var durationSec = etaMinutes != null ? etaMinutes * 60 : null;
        return { latlngs: latlngs, distanceKm: distanceKm, durationSec: durationSec };
      })
      .then(function (out) {
        if (window.team13RouteLine && map) map.removeLayer(window.team13RouteLine);
        window.team13RouteLine = L.polyline(out.latlngs, {
          color: SAGE_GREEN,
          weight: 5,
          lineJoin: 'round',
          lineCap: 'round',
          smoothFactor: 1,
        }).addTo(map);
        map.fitBounds(window.team13RouteLine.getBounds(), { padding: [40, 40] });

        var distanceText = out.distanceKm != null ? 'فاصله: ' + (Math.round(out.distanceKm * 10) / 10) + ' کیلومتر' : '';
        var etaText = out.durationSec != null ? 'زمان تقریبی: ' + formatDuration(out.durationSec) : '';
        return { polyline: window.team13RouteLine, distanceText: distanceText, etaText: etaText };
      });
  }

  function parseRouteGeometry(data, oLat, oLng, tLat, tLng) {
    var latlngs = [];
    var route = data.route || (data.routes && data.routes[0]);
    if (route && route.legs && Array.isArray(route.legs)) {
      route.legs.forEach(function (leg) {
        if (leg.steps && Array.isArray(leg.steps)) {
          leg.steps.forEach(function (step) {
            if (step.polyline && Array.isArray(step.polyline)) {
              step.polyline.forEach(function (c) {
                if (Array.isArray(c) && c.length >= 2) latlngs.push([c[1], c[0]]);
              });
            }
          });
        }
      });
    }
    if (latlngs.length < 2 && data.waypoints && Array.isArray(data.waypoints)) {
      data.waypoints.forEach(function (p) {
        if (Array.isArray(p)) latlngs.push([p[1], p[0]]);
        else if (p && typeof p.lat !== 'undefined') latlngs.push([p.lat, p.lng]);
      });
    }
    if (latlngs.length < 2 && data.routes && data.routes[0] && data.routes[0].geometry && data.routes[0].geometry.coordinates) {
      latlngs = data.routes[0].geometry.coordinates.map(function (c) { return [c[1], c[0]]; });
    }
    if (latlngs.length < 2) latlngs = [[oLat, oLng], [tLat, tLng]];
    return latlngs;
  }

  function parseRouteDistance(data) {
    var route = data.route || (data.routes && data.routes[0]);
    if (route && typeof route.distance === 'number') return route.distance / 1000;
    if (route && route.legs && route.legs[0] && typeof route.legs[0].distance === 'number') {
      var d = 0;
      route.legs.forEach(function (leg) { d += leg.distance || 0; });
      return d / 1000;
    }
    return null;
  }

  function parseRouteDuration(data) {
    var route = data.route || (data.routes && data.routes[0]);
    if (route && typeof route.duration === 'number') return route.duration;
    if (route && route.legs && route.legs[0] && typeof route.legs[0].duration === 'number') {
      var d = 0;
      route.legs.forEach(function (leg) { d += leg.duration || 0; });
      return d;
    }
    return null;
  }

  function parseEtaDuration(data) {
    if (data && typeof data.duration === 'number') return data.duration;
    if (data && data.routes && data.routes[0] && typeof data.routes[0].duration === 'number') return data.routes[0].duration;
    return null;
  }

  function formatDuration(seconds) {
    if (seconds < 60) return seconds + ' ثانیه';
    var m = Math.floor(seconds / 60);
    var s = Math.round(seconds % 60);
    if (s === 0) return m + ' دقیقه';
    return m + ' دقیقه و ' + s + ' ثانیه';
  }

  // --- Sidebar: cards with flyTo on click ---
  function renderPlaceCard(p) {
    var name = (p.name_fa || p.name_en || p.type_display || p.place_id).trim();
    var lat = parseFloat(p.latitude);
    var lng = parseFloat(p.longitude);
    var btn = '<button type="button" class="team13-btn-show-map" data-lat="' + lat + '" data-lng="' + lng + '" data-place-id="' + escapeHtml(p.place_id) + '" data-name="' + escapeHtml(name) + '">نمایش روی نقشه</button>';
    return '<div class="team13-card team13-data-card team13-clickable-card" data-lat="' + lat + '" data-lng="' + lng + '" data-place-id="' + escapeHtml(p.place_id) + '" data-name="' + escapeHtml(name) + '"><p class="font-semibold text-[#1b4332]">' + escapeHtml(name) + '</p><p class="text-sm text-gray-600">' + escapeHtml(p.type_display || '') + (p.city ? ' — ' + escapeHtml(p.city) : '') + '</p>' + btn + '</div>';
  }

  function renderEventCard(e) {
    var title = (e.title_fa || e.title_en || e.event_id).trim();
    var eventId = e.event_id;
    var btn = '<button type="button" class="team13-btn-show-event-on-map" data-event-id="' + escapeHtml(eventId) + '" data-title="' + escapeHtml(title) + '">نمایش روی نقشه</button>';
    return '<div class="team13-card team13-data-card team13-clickable-card" data-event-id="' + escapeHtml(eventId) + '" data-title="' + escapeHtml(title) + '"><p class="font-semibold text-[#1b4332]">' + escapeHtml(title) + '</p><p class="text-sm text-gray-600">' + (e.start_at || e.start_at_iso || '') + (e.city ? ' — ' + escapeHtml(e.city) : '') + '</p>' + btn + '</div>';
  }

  function flyTo(map, lat, lng, zoom) {
    if (!map) return;
    var z = zoom != null ? zoom : (map.getZoom && map.getZoom()) || 14;
    if (map.flyTo) map.flyTo([lat, lng], z, { duration: 0.5 });
    else map.setView([lat, lng], z, { animate: true });
  }

  function haversineKm(lat1, lng1, lat2, lng2) {
    var R = 6371;
    var dLat = (lat2 - lat1) * Math.PI / 180;
    var dLng = (lng2 - lng1) * Math.PI / 180;
    var a = Math.sin(dLat / 2) * Math.sin(dLat / 2) +
      Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) * Math.sin(dLng / 2) * Math.sin(dLng / 2);
    var c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
    return R * c;
  }

  function getCategoryIcon(type) {
    var icons = {
      hotel: '🛏', food: '🍴', restaurant: '🍴', hospital: '🏥', museum: '🎭', entertainment: '🎪',
      fire_station: '🚒', pharmacy: '💊', clinic: '🩺'
    };
    return icons[type] || '📍';
  }

  function renderFacilityCard(place, distanceKm) {
    var name = (place.name_fa || place.name_en || place.type_display || '').trim() || place.place_id;
    var category = place.type_display || place.type || '—';
    var typeKey = (place.type || '').toLowerCase();
    var icon = place.is_user_contributed ? '⭐' : getCategoryIcon(typeKey);
    var rating = place.rating != null ? Number(place.rating) : null;
    var starsHtml = rating != null
      ? ('<span class="team13-facility-stars" aria-label="امتیاز ' + rating + ' از ۵">' + '★'.repeat(Math.round(rating)) + '<span class="team13-facility-stars-empty">' + '☆'.repeat(5 - Math.round(rating)) + '</span></span>')
      : '<span class="text-gray-400 text-sm">—</span>';
    var distText = distanceKm != null ? (distanceKm < 1 ? (Math.round(distanceKm * 1000) + ' م') : (distanceKm.toFixed(1) + ' ک.م')) : '—';
    var lat = parseFloat(place.latitude);
    var lng = parseFloat(place.longitude);
    var placeId = place.place_id || '';
    var userBadge = place.is_user_contributed ? '<span class="team13-facility-user-badge" title="اضافه‌شده توسط کاربر">⭐</span>' : '';
    return '<div class="team13-facility-card team13-clickable-card" data-lat="' + lat + '" data-lng="' + lng + '" data-place-id="' + escapeHtml(placeId) + '" data-name="' + escapeHtml(name) + '">' +
      '<div class="team13-facility-card-head">' +
      '<span class="team13-facility-icon" aria-hidden="true">' + icon + '</span>' +
      '<p class="team13-facility-name font-semibold text-[#1b4332]">' + escapeHtml(name) + userBadge + '</p>' +
      '</div>' +
      '<p class="team13-facility-category text-sm text-gray-600">' + escapeHtml(category) + (place.is_user_contributed ? ' · اضافه‌شده توسط کاربر' : '') + '</p>' +
      '<div class="team13-facility-meta">' + starsHtml + ' <span class="team13-facility-distance">' + escapeHtml(distText) + '</span></div>' +
      '<button type="button" class="team13-btn-show-map" data-lat="' + lat + '" data-lng="' + lng + '" data-place-id="' + escapeHtml(placeId) + '" data-name="' + escapeHtml(name) + '">نمایش روی نقشه</button>' +
      '</div>';
  }

  function getTop5PlacesNearby(places, userLat, userLng) {
    if (!places || !places.length) return [];
    var list = places.map(function (p) {
      var lat = parseFloat(p.latitude);
      var lng = parseFloat(p.longitude);
      var dist = (userLat != null && userLng != null && !isNaN(lat) && !isNaN(lng))
        ? haversineKm(userLat, userLng, lat, lng) : null;
      return { place: p, distanceKm: dist };
    });
    list.sort(function (a, b) {
      var ra = a.place.rating != null ? Number(a.place.rating) : 0;
      var rb = b.place.rating != null ? Number(b.place.rating) : 0;
      if (rb !== ra) return rb - ra;
      if (a.distanceKm != null && b.distanceKm != null) return a.distanceKm - b.distanceKm;
      if (a.distanceKm != null) return -1;
      if (b.distanceKm != null) return 1;
      return 0;
    });
    return list.slice(0, 5);
  }

  function refreshFacilitiesList() {
    var placesList = document.getElementById('places-list');
    var panelPlaces = document.getElementById('panel-places');
    if (!placesList) return;
    var isFacilitiesActive = panelPlaces && panelPlaces.classList.contains('active');
    if (!isFacilitiesActive) return;

    placesList.innerHTML = '<div class="team13-facilities-loading"><span class="team13-facilities-spinner" aria-hidden="true"></span><p class="team13-facilities-loading-text">در حال جستجو...</p></div>';
    var api = window.Team13Api;
    var loadPromise = window._team13PlacesCache && window._team13PlacesCache.length
      ? Promise.resolve({ places: window._team13PlacesCache })
      : (api && api.loadMapData ? api.loadMapData() : Promise.resolve({ places: [] }));
    var userPromise = window.userLocationCoords
      ? Promise.resolve(window.userLocationCoords)
      : (typeof getCurrentPosition === 'function' ? getCurrentPosition() : Promise.reject(new Error('no position'))).then(function (pos) {
          var lat = pos.coords && pos.coords.latitude;
          var lng = pos.coords && pos.coords.longitude;
          if (lat != null && lng != null) window.userLocationCoords = { lat: lat, lng: lng };
          return window.userLocationCoords || { lat: lat, lng: lng };
        }).catch(function () { return null; });

    Promise.all([loadPromise, userPromise]).then(function (results) {
      var places = (results[0] && results[0].places) ? results[0].places : [];
      if (results[0] && results[0].places && results[0].places.length) window._team13PlacesCache = results[0].places;
      var coords = results[1];
      var userLat = coords && coords.lat;
      var userLng = coords && coords.lng;
      var top5 = getTop5PlacesNearby(places, userLat, userLng);
      if (!top5.length) {
        placesList.innerHTML = '<div class="team13-facilities-list"><p class="text-sm text-gray-600 py-4 text-center">مکانی یافت نشد.</p></div>';
        return;
      }
      var html = '<div class="team13-facilities-list">';
      top5.forEach(function (item) {
        html += renderFacilityCard(item.place, item.distanceKm);
      });
      html += '</div>';
      placesList.innerHTML = html;
    }).catch(function () {
      placesList.innerHTML = '<div class="team13-facilities-list"><p class="text-sm text-gray-600 py-4 text-center">خطا در بارگذاری. دوباره تلاش کنید.</p></div>';
    });
  }

  function onPlacesTabActivated() {
    refreshFacilitiesList();
  }

  function injectSidebarCards(places, events) {
    var eventsList = document.getElementById('events-list');
    if (eventsList) {
      eventsList.innerHTML = '';
      (events || []).forEach(function (e) {
        eventsList.insertAdjacentHTML('beforeend', renderEventCard(e));
      });
    }
    var map = getMap();
    function openActionMenuAt(lat, lng, name) {
      flyTo(map, lat, lng);
      if (typeof window.showActionMenu === 'function') window.showActionMenu(lat, lng, name || 'مکان');
    }

    eventsList && eventsList.addEventListener('click', function (ev) {
      var btn = ev.target.closest('.team13-btn-show-event-on-map');
      if (btn) {
        var eventId = btn.getAttribute('data-event-id');
        var title = btn.getAttribute('data-title') || '';
        if (eventId && window.Team13Api && window.Team13Api.api) {
          window.Team13Api.api.eventDetail(eventId).then(function (detail) {
            var lat = detail.latitude != null ? parseFloat(detail.latitude) : NaN;
            var lng = detail.longitude != null ? parseFloat(detail.longitude) : NaN;
            if (!isNaN(lat) && !isNaN(lng)) {
              if (window.allMarkers && window.allMarkers['event-' + eventId]) {
                showPoiMarkerById(map, 'event-' + eventId, lat, lng, false);
              } else {
                openActionMenuAt(lat, lng, title);
              }
            }
          }).catch(function () {});
        }
        if (typeof window.Team13CloseSidebar === 'function') window.Team13CloseSidebar();
        return;
      }
      var card = ev.target.closest('.team13-clickable-card[data-event-id]');
      if (card && window.Team13Api && window.Team13Api.api) {
        var eventId = card.getAttribute('data-event-id');
        var title = card.getAttribute('data-title') || '';
        window.Team13Api.api.eventDetail(eventId).then(function (detail) {
          var lat = detail.latitude != null ? parseFloat(detail.latitude) : NaN;
          var lng = detail.longitude != null ? parseFloat(detail.longitude) : NaN;
          if (!isNaN(lat) && !isNaN(lng)) {
            if (window.allMarkers && window.allMarkers['event-' + eventId]) {
              showPoiMarkerById(map, 'event-' + eventId, lat, lng, false);
            } else {
              openActionMenuAt(lat, lng, title);
            }
          }
        }).catch(function () {});
        if (typeof window.Team13CloseSidebar === 'function') window.Team13CloseSidebar();
      }
    });
  }

  // --- Search (جستجوی آدرس با API جدید بعداً اضافه می‌شود) ---
  var searchDebounceTimer;
  var searchResultMarker = null;
  var favoritePickMarker = null;

  /** به‌روزرسانی لیست نتایج در سایدبار راست (هم جستجوی متنی هم جستجو در محدوده).
   * titleOpt: عنوان اختیاری مثلاً "مکان‌های این محدوده" برای نتایج جستجو در محوطه.
   */
  function updateSidebarResults(items, titleOpt) {
    var sidebarWrap = document.getElementById('team13-sidebar-search-results-wrap');
    var sidebarResultsEl = document.getElementById('team13-sidebar-search-results');
    var sidebarTitle = document.querySelector('#team13-sidebar-search-results-wrap .team13-sidebar-search-results-title');
    if (!sidebarWrap || !sidebarResultsEl) return;
    if (!items || items.length === 0) {
      sidebarWrap.hidden = true;
      sidebarResultsEl.innerHTML = '';
      return;
    }
    renderSearchResults(sidebarResultsEl, items);
    var titleText = (titleOpt && titleOpt.trim()) ? titleOpt.trim() : 'نتایج جستجو';
    if (sidebarTitle) sidebarTitle.textContent = titleText + (items.length ? ' (' + items.length + ')' : '');
    sidebarWrap.hidden = false;
    sidebarWrap.scrollIntoView && sidebarWrap.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
  }

  function initSearch() {
    var input = document.getElementById('team13-search-input');
    var resultsEl = document.getElementById('team13-search-results');
    if (!input || !resultsEl) return;

    input.addEventListener('input', function () {
      clearTimeout(searchDebounceTimer);
      var q = (input.value || '').trim();
      if (q.length < 2) {
        resultsEl.hidden = true;
        resultsEl.innerHTML = '';
        updateSidebarResults([]);
        return;
      }
      searchDebounceTimer = setTimeout(function () {
        var map = getMap();
        var lat, lng;
        if (map && map.getCenter) { var c = map.getCenter(); lat = c.lat; lng = c.lng; }
        mapirAutocomplete(q, lat, lng).then(function (items) {
          renderSearchResults(resultsEl, items);
          resultsEl.hidden = items.length === 0;
          updateSidebarResults(items);
        }).catch(function () {
          resultsEl.hidden = true;
          resultsEl.innerHTML = '';
          updateSidebarResults([]);
        });
      }, 300);
    });

    input.addEventListener('blur', function () {
      setTimeout(function () {
        resultsEl.hidden = true;
      }, 200);
    });

    var btnClearSearch = document.getElementById('team13-clear-search');
    if (btnClearSearch) btnClearSearch.addEventListener('click', function () {
      clearSearchResult();
    });
  }

  var API_BASE = (window.TEAM13_API_BASE || '/team13').replace(/\/$/, '');
  var SEARCH_PLACES_URL = API_BASE + '/search-places/';

  /** جستجو فقط از دیتابیس خودمان (SQLite پروژه) — بدون API نشان. */
  function mapirAutocomplete(text, lat, lng) {
    if (!(text && text.trim())) return Promise.resolve([]);
    var q = text.trim();
    var params = 'q=' + encodeURIComponent(q) + '&limit=50';
    if (lat != null && lng != null && !isNaN(Number(lat)) && !isNaN(Number(lng))) {
      params += '&lat=' + encodeURIComponent(Number(lat)) + '&lng=' + encodeURIComponent(Number(lng));
    }
    function norm(it, keepItemType) {
      var ll = (it.lat != null && it.lng != null) ? { lat: it.lat, lng: it.lng } : (it.y != null && it.x != null) ? { lat: it.y, lng: it.x } : null;
      if (!ll) return null;
      var o = { title: it.title || it.address, address: it.address || it.title, lat: ll.lat, lng: ll.lng, y: ll.lat, x: ll.lng };
      if (keepItemType && it.item_type) o.item_type = it.item_type;
      if (it.place_id) o.place_id = it.place_id;
      return o;
    }
    return fetch(SEARCH_PLACES_URL + '?' + params, { method: 'GET', headers: { Accept: 'application/json' }, credentials: 'same-origin' })
      .then(function (res) {
        if (!res.ok) return [];
        return res.json();
      })
      .then(function (data) {
        var fromDb = (data && data.items) ? data.items : [];
        return fromDb.map(function (it) { return norm(it, true); }).filter(Boolean);
      })
      .catch(function () { return []; });
  }

  function getItemLatLng(item) {
    if (item.y != null && item.x != null) return { lat: parseFloat(item.y), lng: parseFloat(item.x) };
    if (item.lat != null && item.lon != null) return { lat: parseFloat(item.lat), lng: parseFloat(item.lon) };
    if (item.latitude != null && item.longitude != null) return { lat: parseFloat(item.latitude), lng: parseFloat(item.longitude) };
    var geom = item.geom || item.geometry;
    if (geom && geom.coordinates && Array.isArray(geom.coordinates) && geom.coordinates.length >= 2)
      return { lng: parseFloat(geom.coordinates[0]), lat: parseFloat(geom.coordinates[1]) };
    return null;
  }

  function renderSearchResults(container, items) {
    if (!container) return;
    container.innerHTML = '';
    (items || []).forEach(function (item) {
      var title = (item.title || item.address || item.name || item.text || '').trim() || 'مکان';
      var ll = getItemLatLng(item);
      if (!ll) return;
      var lat = ll.lat;
      var lng = ll.lng;
      var isCity = item.item_type === 'city';
      var displayTitle = isCity ? ('شهر ' + title) : title;
      var div = document.createElement('div');
      div.className = 'team13-search-result-item' + (isCity ? ' team13-search-result-city' : '');
      div.textContent = displayTitle;
      div.dataset.lat = lat;
      div.dataset.lng = lng;
      div.dataset.title = displayTitle;
      div.addEventListener('click', function () {
        selectSearchResult(lat, lng, displayTitle);
      });
      container.appendChild(div);
    });
  }

  function selectSearchResult(lat, lng, title) {
    var map = getMap();
    var input = document.getElementById('team13-search-input');
    var resultsEl = document.getElementById('team13-search-results');
    if (input) input.value = title || '';
    if (resultsEl) { resultsEl.hidden = true; resultsEl.innerHTML = ''; }

    setDestFromCoords(lat, lng, title || '');
    var inputDest = document.getElementById('team13-input-dest');
    if (inputDest) inputDest.value = title || '';
    clearTemporaryMapItems(map);
    flyTo(map, lat, lng, 15);
  }

  function clearFavoritePickMarker() {
    var map = getMap();
    if (favoritePickMarker && map && map.hasLayer(favoritePickMarker)) {
      map.removeLayer(favoritePickMarker);
      favoritePickMarker = null;
    }
  }

  function showFavoritePickMarker(lat, lng, title) {
    var map = getMap();
    if (!map) return;
    clearFavoritePickMarker();
    flyTo(map, lat, lng, 15);
    favoritePickMarker = L.marker([lat, lng], { icon: createDestMarkerIcon() }).addTo(map);
    if (title) {
      favoritePickMarker.bindPopup('<div class="team13-popup"><strong>' + escapeHtml(title) + '</strong></div>');
    }
  }

  // --- Emergency: انتخاب موقعیت (زنده یا نقشه) سپس نمایش مراکز در شعاع ۱۰ کیلومتر ---
  var emergencyMarkersLayer = null;
  var emergencyCircleLayer = null;

  function showModalById(id) {
    var el = document.getElementById(id);
    if (!el) return;
    el.hidden = false;
    el.classList.add('team13-modal-open');
    document.body.classList.add('team13-favorite-modal-open');
  }

  function hideModalById(id) {
    var el = document.getElementById(id);
    if (!el) return;
    el.hidden = true;
    el.classList.remove('team13-modal-open');
    document.body.classList.remove('team13-favorite-modal-open');
  }

  /** در صورت ناموفق بودن GPS، جستجوی امداد را با مرکز فعلی نقشه انجام می‌دهد (دیتابیس خودمان). */
  function runEmergencySearchFromMapCenter() {
    var map = getMap();
    if (map && typeof map.getCenter === 'function') {
      var c = map.getCenter();
      if (c && c.lat != null && c.lng != null) {
        runEmergencySearch(c.lat, c.lng);
        return;
      }
    }
    runEmergencySearch(35.6892, 51.3890);
  }

  /** مراکز امدادی: بیمارستان، آتش‌نشانی، داروخانه، کلینیک — با XHR برای اطمینان از نمایش لیست. */
  var EMERGENCY_PLACE_TYPES = 'hospital,fire_station,pharmacy,clinic';
  var EMERGENCY_RADIUS_KM = 10;
  var EMERGENCY_LIMIT = 50;

  function normalizeEmergencyPlace(p) {
    var plat = p && (p.latitude != null) ? parseFloat(p.latitude) : NaN;
    var plng = p && (p.longitude != null) ? parseFloat(p.longitude) : NaN;
    if (isNaN(plat) || isNaN(plng)) return null;
    return {
      place_id: p.place_id,
      type: p.type,
      type_display: p.type_display || p.type || '',
      name_fa: (p.name_fa != null ? String(p.name_fa) : '') || '',
      name_en: (p.name_en != null ? String(p.name_en) : '') || '',
      address: ((p.address || p.city || '') + '').trim() || '',
      city: ((p.city || '') + '').trim() || '',
      latitude: plat,
      longitude: plng,
      distance_km: p.distance_km,
      eta_minutes: p.distance_km != null ? Math.max(1, Math.round(Number(p.distance_km) / 0.5)) : null,
      source: 'db'
    };
  }

  function runEmergencySearch(lat, lng) {
    lat = parseFloat(lat);
    lng = parseFloat(lng);
    if (isNaN(lat) || isNaN(lng)) {
      if (window.showToast) window.showToast('موقعیت انتخاب‌شده نامعتبر است.');
      return;
    }
    var API_BASE = (window.TEAM13_API_BASE || '/team13').replace(/\/$/, '');
    var baseUrl = (window.location.origin || '') + (API_BASE.charAt(0) === '/' ? '' : '/') + API_BASE;
    var placesInRadiusUrl = baseUrl + '/places-in-radius/?format=json&lat=' + encodeURIComponent(lat) + '&lng=' + encodeURIComponent(lng) +
      '&radius_km=' + EMERGENCY_RADIUS_KM + '&type=' + encodeURIComponent(EMERGENCY_PLACE_TYPES) + '&limit=' + EMERGENCY_LIMIT;
    if (window.showToast) window.showToast('در حال جستجوی مراکز امدادی (بیمارستان، آتش‌نشانی، داروخانه، کلینیک) در شعاع ۱۰ کیلومتر…');
    var xhr = new XMLHttpRequest();
    xhr.open('GET', placesInRadiusUrl, true);
    xhr.setRequestHeader('Accept', 'application/json');
    xhr.timeout = 30000;
    xhr.withCredentials = true;
    xhr.onreadystatechange = function () {
      if (xhr.readyState !== 4) return;
      var places = [];
      if (xhr.status === 200 && xhr.responseText) {
        try {
          var data = JSON.parse(xhr.responseText);
          var raw = (data && data.places) ? data.places : [];
          if (Array.isArray(raw)) {
            for (var i = 0; i < raw.length; i++) {
              var item = normalizeEmergencyPlace(raw[i]);
              if (item) places.push(item);
            }
          }
        } catch (e) {
          if (window.console && window.console.warn) window.console.warn('امداد: پارس JSON', e);
        }
      }
      if (xhr.status !== 200 && window.showToast) window.showToast('خطا در دریافت مراکز امدادی از دیتابیس. لطفاً دوباره تلاش کنید.');
      try { showEmergencyResults(lat, lng, places); } catch (err) {
        if (window.console && window.console.warn) window.console.warn('showEmergencyResults', err);
        showEmergencyResults(lat, lng, []);
      }
    };
    xhr.onerror = function () {
      if (window.showToast) window.showToast('خطا در دریافت مراکز امدادی از دیتابیس. لطفاً دوباره تلاش کنید.');
      try { showEmergencyResults(lat, lng, []); } catch (e) {}
    };
    xhr.ontimeout = function () {
      if (window.showToast) window.showToast('زمان درخواست تمام شد. دوباره تلاش کنید.');
      try { showEmergencyResults(lat, lng, []); } catch (e) {}
    };
    xhr.send();
  }

  function showEmergencyResults(centerLat, centerLng, places) {
    var map = getMap();
    if (map && emergencyCircleLayer) {
      try { map.removeLayer(emergencyCircleLayer); } catch (e) {}
      emergencyCircleLayer = null;
    }
    if (map && emergencyMarkersLayer) {
      try { emergencyMarkersLayer.clearLayers && emergencyMarkersLayer.clearLayers(); } catch (e) {}
      try { map.removeLayer(emergencyMarkersLayer); } catch (e) {}
      emergencyMarkersLayer = null;
    }
    if (window.emergencyPoiMarker && map && typeof map.hasLayer === 'function' && map.hasLayer(window.emergencyPoiMarker)) {
      try { map.removeLayer(window.emergencyPoiMarker); } catch (e) {}
      window.emergencyPoiMarker = null;
    }
    if (map && L && typeof L.circle === 'function') {
      emergencyCircleLayer = L.circle([centerLat, centerLng], {
        radius: EMERGENCY_RADIUS_KM * 1000,
        color: '#dc2626',
        fillColor: '#dc2626',
        fillOpacity: 0.12,
        weight: 2,
      });
      emergencyCircleLayer.addTo(map);
    }
    emergencyMarkersLayer = L && typeof L.layerGroup === 'function' ? L.layerGroup() : null;
    var minLat = centerLat, maxLat = centerLat, minLng = centerLng, maxLng = centerLng;
    if (map && emergencyMarkersLayer && L && typeof L.marker === 'function') {
      (places || []).forEach(function (p) {
        var lat = parseFloat(p.latitude || p.lat);
        var lng = parseFloat(p.longitude || p.lng);
        if (isNaN(lat) || isNaN(lng)) return;
        if (lat < minLat) minLat = lat;
        if (lat > maxLat) maxLat = lat;
        if (lng < minLng) minLng = lng;
        if (lng > maxLng) maxLng = lng;
        var name = (p.name_fa || p.type_display || '').trim() || 'مرکز امدادی';
        var icon = createEmergencyPoiIcon();
        if (!icon) return;
        var m = L.marker([lat, lng], { icon: icon }).bindPopup(
          '<div class="team13-popup" dir="rtl"><strong>' + escapeHtml(name) + '</strong><br><span class="text-muted">' + escapeHtml(p.type_display || '') + ' — ' + (p.distance_km != null ? p.distance_km + ' ک.م' : '') + '</span></div>'
        );
        emergencyMarkersLayer.addLayer(m);
        if (typeof m.addTo === 'function') m.addTo(map);
      });
      if (places && places.length > 0 && (minLat !== maxLat || minLng !== maxLng)) {
        try {
          map.fitBounds({
            getSouthWest: function () { return { lat: minLat, lng: minLng }; },
            getNorthEast: function () { return { lat: maxLat, lng: maxLng }; }
          }, { padding: [40, 40], maxZoom: 14 });
        } catch (e) {
          if (centerLat != null && centerLng != null && typeof map.flyTo === 'function') map.flyTo({ lat: centerLat, lng: centerLng }, 12);
        }
      } else if (centerLat != null && centerLng != null && typeof map.flyTo === 'function') {
        map.flyTo({ lat: centerLat, lng: centerLng }, 12);
      }
    }
    var listEl = document.getElementById('team13-emergency-results-list');
    if (listEl) {
      if (!places || places.length === 0) {
        listEl.innerHTML = '<p class="team13-emergency-no-results">مرکزی در شعاع ۱۰ کیلومتر یافت نشد.</p>';
      } else {
        var html = '';
        places.forEach(function (p) {
          var name = (p.name_fa || p.type_display || '').trim() || 'مرکز امدادی';
          var dist = p.distance_km != null ? p.distance_km + ' ک.م' : '';
          html += '<div class="team13-emergency-result-item" data-lat="' + p.latitude + '" data-lng="' + p.longitude + '">' +
            '<strong>' + escapeHtml(name) + '</strong>' +
            '<span class="team13-emergency-type">' + escapeHtml(p.type_display || '') + '</span>' +
            (dist ? '<span class="team13-emergency-dist">' + escapeHtml(dist) + '</span>' : '') +
            '<p class="team13-emergency-address">' + escapeHtml(p.address || '—') + '</p></div>';
        });
        listEl.innerHTML = html;
      }
    }
    showModalById('team13-modal-emergency-results');
  }

  function initEmergencyButtons() {
    var btnEmergency = document.getElementById('team13-btn-emergency');
    if (btnEmergency) {
      btnEmergency.addEventListener('click', function () {
        showModalById('team13-modal-emergency-source');
      });
    }
    var btnUseLive = document.getElementById('team13-emergency-use-live');
    if (btnUseLive) {
      btnUseLive.addEventListener('click', function () {
        hideModalById('team13-modal-emergency-source');
        if (!navigator.geolocation) {
          if (window.showToast) window.showToast('موقعیت جغرافیایی پشتیبانی نمی‌شود. جستجو بر اساس مرکز نقشه انجام می‌شود.');
          runEmergencySearchFromMapCenter();
          return;
        }
        if (window.showToast) window.showToast('در حال دریافت موقعیت…');
        navigator.geolocation.getCurrentPosition(
          function (pos) {
            runEmergencySearch(pos.coords.latitude, pos.coords.longitude);
          },
          function (err) {
            var msg = err && err.code === 1 ? 'دسترسی به موقعیت رد شد.' : err && err.code === 3 ? 'زمان درخواست موقعیت تمام شد.' : 'موقعیت در دسترس نبود.';
            if (window.showToast) window.showToast(msg + ' جستجو بر اساس مرکز نقشه انجام می‌شود.');
            runEmergencySearchFromMapCenter();
          },
          { enableHighAccuracy: false, timeout: 12000, maximumAge: 60000 }
        );
      });
    }
    var btnPickMap = document.getElementById('team13-emergency-pick-map');
    if (btnPickMap) {
      btnPickMap.addEventListener('click', function () {
        hideModalById('team13-modal-emergency-source');
        window._team13EmergencyPickMode = true;
        if (window.showToast) window.showToast('روی نقشه کلیک کنید تا نقطهٔ جستجو انتخاب شود.');
      });
    }
    var btnHospital = document.getElementById('team13-btn-nearest-hospital');
    var btnFire = document.getElementById('team13-btn-nearest-fire');
    if (btnHospital) btnHospital.addEventListener('click', triggerNearestHospital);
    if (btnFire) btnFire.addEventListener('click', triggerNearestFireStation);
  }

  /**
   * Emergency: find nearest POI, clear other markers, draw multi-point route, show only that POI marker.
   * @param {string} category - "بیمارستان" or "آتش نشانی"
   */
  function triggerNearestPoi(category) {
    var map = getMap();
    setRouteLoading(true);
    hideRouteInfo();
    clearTemporaryMapItems(map);
    if (!window.Team13Api || typeof window.Team13Api.findNearest !== 'function' || typeof window.Team13Api.getRouteFromUserToPoint !== 'function') {
      setRouteLoading(false);
      showRouteInfo('خطا: سرویس مسیریابی در دسترس نیست', '');
      return;
    }
    window.Team13Api.findNearest(category)
      .then(function (poi) {
        if (!poi || poi.lat == null || poi.lng == null) throw new Error(category === 'بیمارستان' ? 'بیمارستانی یافت نشد' : 'آتش‌نشانی یافت نشد');
        if (map && window.emergencyPoiMarker && map.hasLayer(window.emergencyPoiMarker)) map.removeLayer(window.emergencyPoiMarker);
        window.emergencyPoiMarker = L.marker([poi.lat, poi.lng], { icon: createEmergencyPoiIcon() })
          .bindPopup('<div class="team13-popup"><strong>' + escapeHtml(poi.title || category) + '</strong></div>');
        window.emergencyPoiMarker.addTo(map);
        return window.Team13Api.getRouteFromUserToPoint({ lat: poi.lat, lng: poi.lng }, 'driving');
      })
      .then(function (r) {
        setRouteLoading(false);
        if (typeof window.updateRouteInfoBox === 'function') window.updateRouteInfoBox(r);
      })
      .catch(function (err) {
        setRouteLoading(false);
        if (window.emergencyPoiMarker && map && map.hasLayer(window.emergencyPoiMarker)) {
          map.removeLayer(window.emergencyPoiMarker);
          window.emergencyPoiMarker = null;
        }
        showRouteInfo('خطا: ' + (err && err.message ? err.message : (category === 'بیمارستان' ? 'بیمارستان' : 'آتش‌نشانی') + ' یافت نشد'), '');
        clearTimeout(window._team13EmergencyErrorDismiss);
        window._team13EmergencyErrorDismiss = setTimeout(function () {
          var box = document.getElementById('team13-route-info');
          if (box) {
            box.classList.add('team13-route-info-fade-out');
            setTimeout(function () {
              hideRouteInfo();
              box.classList.remove('team13-route-info-fade-out');
            }, 500);
          }
        }, 5000);
      });
  }

  function triggerNearestHospital() {
    triggerNearestPoi('بیمارستان');
  }

  function triggerNearestFireStation() {
    triggerNearestPoi('آتش نشانی');
  }

  // --- Start/Destination routing state ---
  var startCoords = null;
  var startAddress = '';
  var destCoords = null;
  var destAddress = '';
  var startMarker = null;
  var destMarker = null;
  var pickMode = null;
  var routeMode = 'driving';
  var reverseGeocodeMarker = null;

  function setRouteMode(mode) {
    routeMode = (mode || 'driving').toLowerCase();
    var wrap = document.getElementById('team13-route-mode-wrap');
    if (wrap) {
      wrap.querySelectorAll('.team13-route-mode-btn').forEach(function (b) {
        b.classList.remove('active', 'active-transport');
        if ((b.getAttribute('data-mode') || '') === routeMode) b.classList.add('active', 'active-transport');
      });
    }
  }

  /** Update crosshair cursor class on map container when any point-selection mode is active. */
  function updateSelectionActiveCursor() {
    var active = !!(window.isPlacementMode || pickMode || pickModeDiscovery);
    var container = document.getElementById('map-container');
    if (container) {
      if (active) container.classList.add('selection-active');
      else container.classList.remove('selection-active');
    }
  }

  function setPickMode(mode) {
    pickMode = mode;
    updateSelectionActiveCursor();
    var btnStart = document.getElementById('team13-btn-pick-start');
    var btnDest = document.getElementById('team13-btn-pick-dest');
    if (btnStart) btnStart.classList.toggle('active', mode === 'start');
    if (btnDest) btnDest.classList.toggle('active', mode === 'dest');
  }

  function syncRouteInputHasText(inputId) {
    var input = document.getElementById(inputId);
    if (!input) return;
    var wrap = input.closest ? input.closest('.team13-input-with-clear') : input.parentNode;
    if (!wrap || !wrap.classList) return;
    if ((input.value || '').trim()) wrap.classList.add('team13-has-text');
    else wrap.classList.remove('team13-has-text');
  }

  function setStartFromCoords(lat, lng, address) {
    startCoords = { lat: lat, lng: lng };
    startAddress = address || '';
    var input = document.getElementById('team13-input-start');
    if (input) input.value = startAddress;
    syncRouteInputHasText('team13-input-start');
    var map = getMap();
    if (map && startMarker) map.removeLayer(startMarker);
    startMarker = L.marker([lat, lng], { icon: createStartMarkerIcon(), draggable: true })
      .on('dragend', function () {
        var pos = startMarker.getLatLng();
        startCoords = { lat: pos.lat, lng: pos.lng };
        window.Team13Api.reverseGeocode(pos.lat, pos.lng).then(function (data) {
          startAddress = (data && (data.address || data.address_compact || data.postal_address)) || '';
          var inp = document.getElementById('team13-input-start');
          if (inp) inp.value = startAddress;
          syncRouteInputHasText('team13-input-start');
          drawRouteFromToIfBoth();
        });
      })
      .addTo(map);
    drawRouteFromToIfBoth();
  }

  function setDestFromCoords(lat, lng, address) {
    destCoords = { lat: lat, lng: lng };
    destAddress = address || '';
    var input = document.getElementById('team13-input-dest');
    if (input) input.value = destAddress;
    syncRouteInputHasText('team13-input-dest');
    var topInput = document.getElementById('team13-search-input');
    if (topInput) topInput.value = destAddress;
    var map = getMap();
    if (map && destMarker) map.removeLayer(destMarker);
    destMarker = L.marker([lat, lng], { icon: createDestMarkerIcon(), draggable: true })
      .on('dragend', function () {
        var pos = destMarker.getLatLng();
        destCoords = { lat: pos.lat, lng: pos.lng };
        window.Team13Api.reverseGeocode(pos.lat, pos.lng).then(function (data) {
          destAddress = (data && (data.address || data.address_compact || data.postal_address)) || '';
          var inp = document.getElementById('team13-input-dest');
          if (inp) inp.value = destAddress;
          var top = document.getElementById('team13-search-input');
          if (top) top.value = destAddress;
          syncRouteInputHasText('team13-input-dest');
          drawRouteFromToIfBoth();
        });
      })
      .addTo(map);
    drawRouteFromToIfBoth();
  }

  function drawRouteFromToIfBoth() {
    if (!startCoords || !destCoords || !window.Team13Api || typeof window.Team13Api.getRouteFromTo !== 'function') return null;
    var clearWrap = document.getElementById('team13-clear-route-wrap');
    var clearBtn = document.getElementById('team13-btn-clear-path');
    if (clearWrap) clearWrap.style.display = '';
    else if (clearBtn) clearBtn.style.display = 'block';
    return window.Team13Api.getRouteFromTo(startCoords, destCoords, routeMode)
      .then(function (r) {
        if (typeof window.updateRouteInfoBox === 'function') window.updateRouteInfoBox(r);
        if (typeof window.Team13MapCleanup === 'function') window.Team13MapCleanup();
        return r;
      })
      .catch(function (err) {
        if (typeof window.updateRouteInfoBox === 'function') window.updateRouteInfoBox(null);
        if (typeof window.showToast === 'function') window.showToast('خطا: ' + (err && err.message ? err.message : 'مسیریابی ناموفق'));
        throw err;
      });
  }

  function clearRouteLine() {
    var map = getMap();
    [window.currentPath, window.routeLayer, window.currentRoute, window.team13RouteLine].forEach(function (layer) {
      if (layer && map && map.hasLayer(layer)) map.removeLayer(layer);
    });
    window.currentPath = null;
    window.routeLayer = null;
    window.currentRoute = null;
    window.team13RouteLine = null;
    hideRouteInfo();
    if (typeof window.updateRouteInfoBox === 'function') window.updateRouteInfoBox(null);
    var clearWrap = document.getElementById('team13-clear-route-wrap');
    var clearBtn = document.getElementById('team13-btn-clear-path');
    if (clearWrap) clearWrap.style.display = 'none';
    else if (clearBtn) clearBtn.style.display = 'none';
  }

  function clearStart() {
    startCoords = null;
    startAddress = '';
    var input = document.getElementById('team13-input-start');
    if (input) input.value = '';
    syncRouteInputHasText('team13-input-start');
    var map = getMap();
    if (startMarker && map && map.hasLayer(startMarker)) {
      map.removeLayer(startMarker);
    }
    startMarker = null;
    clearRouteLine();
  }

  function clearDest() {
    destCoords = null;
    destAddress = '';
    var input = document.getElementById('team13-input-dest');
    if (input) input.value = '';
    syncRouteInputHasText('team13-input-dest');
    var topInput = document.getElementById('team13-search-input');
    if (topInput) topInput.value = '';
    var map = getMap();
    if (destMarker && map && map.hasLayer(destMarker)) {
      map.removeLayer(destMarker);
    }
    destMarker = null;
    clearRouteLine();
  }

  function swapStartDest() {
    var sC = startCoords;
    var sA = startAddress;
    var dC = destCoords;
    var dA = destAddress;
    startCoords = dC;
    startAddress = dA || '';
    destCoords = sC;
    destAddress = sA || '';
    var inputStart = document.getElementById('team13-input-start');
    var inputDest = document.getElementById('team13-input-dest');
    var topInput = document.getElementById('team13-search-input');
    if (inputStart) inputStart.value = startAddress;
    if (inputDest) inputDest.value = destAddress;
    if (topInput) topInput.value = destAddress;
    var map = getMap();
    if (startMarker && map && map.hasLayer(startMarker)) map.removeLayer(startMarker);
    if (destMarker && map && map.hasLayer(destMarker)) map.removeLayer(destMarker);
    startMarker = null;
    destMarker = null;
    if (startCoords && map) {
      startMarker = L.marker([startCoords.lat, startCoords.lng], { icon: createStartMarkerIcon(), draggable: true })
        .on('dragend', function () {
          var pos = startMarker.getLatLng();
          startCoords = { lat: pos.lat, lng: pos.lng };
          window.Team13Api.reverseGeocode(pos.lat, pos.lng).then(function (data) {
            startAddress = (data && (data.address || data.address_compact || data.postal_address)) || '';
            var inp = document.getElementById('team13-input-start');
            if (inp) inp.value = startAddress;
            drawRouteFromToIfBoth();
          });
        })
        .addTo(map);
    }
    if (destCoords && map) {
      destMarker = L.marker([destCoords.lat, destCoords.lng], { icon: createDestMarkerIcon(), draggable: true })
        .on('dragend', function () {
          var pos = destMarker.getLatLng();
          destCoords = { lat: pos.lat, lng: pos.lng };
          window.Team13Api.reverseGeocode(pos.lat, pos.lng).then(function (data) {
            destAddress = (data && (data.address || data.address_compact || data.postal_address)) || '';
            var inp = document.getElementById('team13-input-dest');
            if (inp) inp.value = destAddress;
            var top = document.getElementById('team13-search-input');
            if (top) top.value = destAddress;
            drawRouteFromToIfBoth();
          });
        })
        .addTo(map);
    }
    drawRouteFromToIfBoth();
  }

  function initStartDestUI() {
    var inputStart = document.getElementById('team13-input-start');
    var inputDest = document.getElementById('team13-input-dest');
    var resultsStart = document.getElementById('team13-start-results');
    var resultsDest = document.getElementById('team13-dest-results');
    var btnPickStart = document.getElementById('team13-btn-pick-start');
    var btnPickDest = document.getElementById('team13-btn-pick-dest');
    var btnMyLocation = document.getElementById('team13-btn-my-location');
    var modeWrap = document.getElementById('team13-route-mode-wrap');
    if (!inputStart || !inputDest) return;

    function bindAutocomplete(inputEl, resultsEl, setter) {
      if (!inputEl || !resultsEl) return;
      var debounce;
      inputEl.addEventListener('input', function () {
        clearTimeout(debounce);
        var q = (inputEl.value || '').trim();
        if (q.length < 2) { resultsEl.hidden = true; resultsEl.innerHTML = ''; return; }
        debounce = setTimeout(function () {
          var map = getMap();
          var lat, lng;
          if (map && map.getCenter) { var c = map.getCenter(); lat = c.lat; lng = c.lng; }
          mapirAutocomplete(q, lat, lng).then(function (items) {
            resultsEl.innerHTML = '';
            items.forEach(function (item) {
              var title = (item.title || item.address || item.name || item.text || '').trim();
              var ll = getItemLatLng(item);
              if (!ll) return;
              var div = document.createElement('div');
              div.className = 'team13-search-result-item';
              div.textContent = title;
              div.dataset.lat = ll.lat;
              div.dataset.lng = ll.lng;
              div.dataset.title = title;
              div.addEventListener('click', function () {
                setter(ll.lat, ll.lng, title);
                resultsEl.hidden = true;
                resultsEl.innerHTML = '';
              });
              resultsEl.appendChild(div);
            });
            resultsEl.hidden = items.length === 0;
          });
        }, 300);
      });
      inputEl.addEventListener('blur', function () {
        setTimeout(function () { resultsEl.hidden = true; }, 200);
      });
    }

    bindAutocomplete(inputStart, resultsStart, setStartFromCoords);
    bindAutocomplete(inputDest, resultsDest, setDestFromCoords);

    function syncClearHasText(inputEl) {
      var wrap = inputEl && inputEl.closest ? inputEl.closest('.team13-input-with-clear') : (inputEl && inputEl.parentNode);
      if (!wrap) return;
      if ((inputEl.value || '').trim()) wrap.classList.add('team13-has-text');
      else wrap.classList.remove('team13-has-text');
    }
    if (inputStart) {
      inputStart.addEventListener('input', function () { syncClearHasText(inputStart); });
      inputStart.addEventListener('change', function () { syncClearHasText(inputStart); });
      syncClearHasText(inputStart);
    }
    if (inputDest) {
      inputDest.addEventListener('input', function () { syncClearHasText(inputDest); });
      inputDest.addEventListener('change', function () { syncClearHasText(inputDest); });
      syncClearHasText(inputDest);
    }

    if (btnPickStart) {
      btnPickStart.addEventListener('click', function () {
        setPickMode(pickMode === 'start' ? null : 'start');
      });
    }
    if (btnPickDest) {
      btnPickDest.addEventListener('click', function () {
        setPickMode(pickMode === 'dest' ? null : 'dest');
      });
    }
    if (btnMyLocation) {
      btnMyLocation.addEventListener('click', function () {
        if (!navigator.geolocation) {
          if (window.showToast) window.showToast('مرورگر از موقعیت جغرافیایی پشتیبانی نمی‌کند');
          return;
        }
        if (window.showToast) window.showToast('در حال دریافت موقعیت فعلی...');
        navigator.geolocation.getCurrentPosition(
          function (pos) {
            var lat = pos.coords.latitude;
            var lng = pos.coords.longitude;
            window.Team13Api.reverseGeocode(lat, lng).then(function (data) {
              var addr = (data && (data.address || data.address_compact || data.postal_address)) || '';
              setStartFromCoords(lat, lng, addr);
              if (window.showToast) window.showToast('مبدا روی موقعیت شما تنظیم شد');
            }).catch(function () {
              setStartFromCoords(lat, lng, 'موقعیت من');
              if (window.showToast) window.showToast('مبدا روی موقعیت شما تنظیم شد');
            });
          },
          function (e) {
            var msg = e.code === 1 ? 'دسترسی به موقعیت رد شد. در تنظیمات مرورگر اجازهٔ مکان را فعال کنید.' : e.code === 2 ? 'موقعیت در دسترس نیست.' : e.code === 3 ? 'زمان درخواست تمام شد.' : 'دسترسی به موقعیت امکان‌پذیر نیست';
            if (window.showToast) window.showToast(msg);
          },
          { enableHighAccuracy: true, timeout: 20000, maximumAge: 0 }
        );
      });
    }
    if (modeWrap) {
      modeWrap.querySelectorAll('.team13-route-mode-btn').forEach(function (btn) {
        btn.addEventListener('click', function () {
          routeMode = this.getAttribute('data-mode') || 'driving';
          modeWrap.querySelectorAll('.team13-route-mode-btn').forEach(function (b) {
            b.classList.remove('active', 'active-transport');
          });
          this.classList.add('active', 'active-transport');
          drawRouteFromToIfBoth();
          if (typeof window.Team13CloseSidebar === 'function') window.Team13CloseSidebar();
        });
      });
    }

    var btnClearStart = document.getElementById('team13-clear-start');
    var btnClearDest = document.getElementById('team13-clear-dest');
    var btnSwap = document.getElementById('team13-btn-swap-route');
    if (btnClearStart) btnClearStart.addEventListener('click', clearStart);
    if (btnClearDest) btnClearDest.addEventListener('click', clearDest);
    if (btnSwap) {
      btnSwap.addEventListener('click', function () {
        swapStartDest();
        btnSwap.classList.toggle('team13-swap-route-rotated');
      });
    }
    var btnCalcRoute = document.getElementById('team13-btn-calc-route');
    var calcRouteText = btnCalcRoute ? btnCalcRoute.querySelector('.team13-btn-calc-route-text') : null;
    var calcRouteSpinner = btnCalcRoute ? btnCalcRoute.querySelector('.team13-btn-calc-route-spinner') : null;
    if (btnCalcRoute) {
      btnCalcRoute.addEventListener('click', function () {
        if (!startCoords || !destCoords) {
          if (window.showToast) window.showToast('مبدا و مقصد را انتخاب کنید.');
          return;
        }
        if (btnCalcRoute.disabled) return;
        btnCalcRoute.disabled = true;
        btnCalcRoute.classList.add('team13-btn-calc-route-loading');
        if (calcRouteText) calcRouteText.textContent = 'در حال محاسبه...';
        if (calcRouteSpinner) calcRouteSpinner.hidden = false;
        var p = drawRouteFromToIfBoth();
        function done() {
          btnCalcRoute.disabled = false;
          btnCalcRoute.classList.remove('team13-btn-calc-route-loading');
          if (calcRouteText) calcRouteText.textContent = 'مسیریابی';
          if (calcRouteSpinner) calcRouteSpinner.hidden = true;
        }
        if (p && typeof p.then === 'function') {
          p.then(done).catch(done);
        } else {
          setTimeout(done, 1500);
        }
      });
    }
  }

  function onMapClickForStartDest(e) {
    if (!pickMode || pickMode !== 'start' && pickMode !== 'dest') return false;
    var map = getMap();
    if (!map || !e || !e.latlng) return true;
    var lat = e.latlng.lat;
    var lng = e.latlng.lng;
    var mode = pickMode;
    setPickMode(null);
    window.Team13Api.reverseGeocode(lat, lng)
      .then(function (data) {
        var addr = (data && (data.address || data.address_compact || data.postal_address)) || '';
        if (mode === 'start') setStartFromCoords(lat, lng, addr);
        else setDestFromCoords(lat, lng, addr);
      })
      .catch(function () {
        if (mode === 'start') setStartFromCoords(lat, lng, '');
        else setDestFromCoords(lat, lng, '');
      });
    return true;
  }

  // --- Placement mode: add pointer only when user has toggled it via "Select Point" button ---
  function setPlacementModeActive(active) {
    window.isPlacementMode = !!active;
    updateSelectionActiveCursor();
    var btn = document.getElementById('team13-btn-add-pointer');
    if (btn) btn.classList.toggle('active-btn', active);
  }

  // --- Map click: show green button only; second click (on button) → nearest-place then register or rate/photo ---
  // Ensure clicks on markers/popups do not trigger placement or other map-click logic (event priority).
  function initReverseGeocodeClick() {
    var map = getMap();
    if (!map || !window.Team13Api) return;
    map.off('click', onMapClickReverseGeocode);
    map.on('click', onMapClickReverseGeocode);

    var container = document.getElementById('map-container');
    if (container && !container._team13CaptureClickInstalled) {
      container._team13CaptureClickInstalled = true;
      container.addEventListener('click', function (e) {
        var target = e.target;
        if (target && typeof target.closest === 'function') {
          if (target.closest('.mapboxgl-marker') || target.closest('.team13-neshan-marker') ||
              target.closest('.mapboxgl-popup') || target.closest('.team13-reverse-popup-content') ||
              target.closest('.team13-reverse-popup') || target.closest('.team13-place-marker')) {
            window._team13ClickOnMarkerOrPopup = true;
          }
        }
        setTimeout(function () { window._team13ClickOnMarkerOrPopup = false; }, 0);
      }, true);
    }
  }

  /** پاپ‌آپ دکمهٔ سبز: یک دکمه «ادامه»؛ با کلیک روی آن nearest-place صدا زده می‌شود و بر اساس نتیجه ثبت مکان یا امتیاز/عکس. */
  function buildGreenButtonPopupContent(lat, lng, markerRef, mapRef) {
    var wrap = document.createElement('div');
    wrap.className = 'team13-reverse-popup-content';
    wrap.setAttribute('dir', 'rtl');
    wrap.innerHTML =
      '<p class="team13-reverse-popup-address">این نقطه انتخاب شد. برای ثبت مکان جدید روی «ادامه» بزنید و در فرم <strong>آدرس</strong> و مشخصات را وارد کنید.</p>' +
      '<div class="team13-reverse-popup-actions">' +
      '<button type="button" class="team13-reverse-popup-btn team13-reverse-popup-btn-green">ادامه</button>' +
      '</div>' +
      '<div class="team13-reverse-popup-footer">' +
      '<button type="button" class="team13-reverse-popup-delete-link">حذف نقطه</button>' +
      '</div>';
    var btnGreen = wrap.querySelector('.team13-reverse-popup-btn-green');
    var btnDelete = wrap.querySelector('.team13-reverse-popup-delete-link');
    if (btnGreen) {
      btnGreen.addEventListener('click', function () {
        if (!window.Team13Api || typeof window.Team13Api.fetchData !== 'function') return;
        var params = { lat: String(lat), lng: String(lng), radius_km: '0.05' };
        window.Team13Api.fetchData('nearest-place/', params)
          .then(function (data) {
            if (!data) data = {};
            var place = data.place;
            if (!place) {
              if (!window.confirm('آیا می‌خواهید در این نقطه موقعیتی ثبت کنید؟')) {
                clearReverseGeocodeMarker();
                return;
              }
              if (typeof window.Team13OpenContributionModal === 'function') {
                window.Team13OpenContributionModal(lat, lng);
              }
              clearReverseGeocodeMarker();
              return;
            }
            var placeId = place.place_id;
            var name = place.name_fa || place.name_en || 'مکان';
            if (typeof window.Team13OpenPlaceActionsModal === 'function') {
              window.Team13OpenPlaceActionsModal(placeId, name, lat, lng);
            }
            clearReverseGeocodeMarker();
          })
          .catch(function () {
            if (window.showToast) window.showToast('خطا در ارتباط با سرور.');
          });
      });
    }
    if (btnDelete) {
      btnDelete.addEventListener('click', function () { clearReverseGeocodeMarker(); });
    }
    return wrap;
  }

  function buildReversePopupContent(lat, lng, address, markerRef, mapRef) {
    var wrap = document.createElement('div');
    wrap.className = 'team13-reverse-popup-content';
    wrap.setAttribute('dir', 'rtl');
    wrap.innerHTML =
      '<p class="team13-reverse-popup-address">' + escapeHtml(address) + '</p>' +
      '<div class="team13-reverse-popup-actions">' +
      '<button type="button" class="team13-reverse-popup-btn team13-reverse-popup-btn-fav"><span class="team13-popup-star" aria-hidden="true">⭐</span> افزودن به علاقه‌مندی</button>' +
      '<button type="button" class="team13-reverse-popup-btn team13-reverse-popup-btn-start">تعیین به عنوان مبدا</button>' +
      '<button type="button" class="team13-reverse-popup-btn team13-reverse-popup-btn-dest">تعیین به عنوان مقصد</button>' +
      '</div>' +
      '<div class="team13-reverse-popup-footer">' +
      '<button type="button" class="team13-reverse-popup-delete-link">حذف نقطه</button>' +
      '</div>';
    var btnFav = wrap.querySelector('.team13-reverse-popup-btn-fav');
    var btnStart = wrap.querySelector('.team13-reverse-popup-btn-start');
    var btnDest = wrap.querySelector('.team13-reverse-popup-btn-dest');
    var btnDelete = wrap.querySelector('.team13-reverse-popup-delete-link');
    if (btnFav) {
      btnFav.addEventListener('click', function () {
        if (typeof window.Team13OpenAddFavoriteWithLocation === 'function') {
          window.Team13OpenAddFavoriteWithLocation(lat, lng, address);
        }
      });
    }
    if (btnStart) {
      btnStart.addEventListener('click', function () {
        if (typeof window.Team13OpenSidebarAndRouteTab === 'function') window.Team13OpenSidebarAndRouteTab();
        setStartFromCoords(lat, lng, address);
      });
    }
    if (btnDest) {
      btnDest.addEventListener('click', function () {
        if (typeof window.Team13OpenSidebarAndRouteTab === 'function') window.Team13OpenSidebarAndRouteTab();
        setDestFromCoords(lat, lng, address);
      });
    }
    if (btnDelete) {
      btnDelete.addEventListener('click', function () {
        clearReverseGeocodeMarker();
      });
    }
    return wrap;
  }

  function clearReverseGeocodeMarker() {
    var map = getMap();
    if (reverseGeocodeMarker && map && map.hasLayer(reverseGeocodeMarker)) {
      map.removeLayer(reverseGeocodeMarker);
    }
    reverseGeocodeMarker = null;
  }

  function onMapClickReverseGeocode(e) {
    if (window._team13ClickOnMarkerOrPopup) {
      window._team13ClickOnMarkerOrPopup = false;
      return;
    }
    if (window._team13EmergencyPickMode && e && e.latlng) {
      window._team13EmergencyPickMode = false;
      runEmergencySearch(e.latlng.lat, e.latlng.lng);
      return;
    }
    if (onMapClickForDiscovery(e)) return;
    if (onMapClickForStartDest(e)) return;
    if (window._team13PickForFavorite && typeof window._team13PickForFavorite === 'function') {
      var cb = window._team13PickForFavorite;
      window._team13PickForFavorite = null;
      var lat = e.latlng.lat;
      var lng = e.latlng.lng;
      cb(lat, lng);
      return;
    }
    if (window._team13ContributionPickMode && e && e.latlng) {
      window._team13ContributionPickMode = false;
      var map = getMap();
      if (!map) return;
      var lat = e.latlng.lat;
      var lng = e.latlng.lng;
      if (reverseGeocodeMarker && map.hasLayer(reverseGeocodeMarker)) {
        map.removeLayer(reverseGeocodeMarker);
        reverseGeocodeMarker = null;
      }
      var markerIcon = L.divIcon({
        className: 'team13-reverse-marker',
        html: '<span style="width:22px;height:22px;background:#40916c;border:2px solid #1b4332;border-radius:50%;display:block;box-shadow:0 2px 8px rgba(0,0,0,0.3);"></span>',
        iconSize: [22, 22],
        iconAnchor: [11, 11],
      });
      reverseGeocodeMarker = L.marker([lat, lng], { icon: markerIcon }).addTo(map);
      var wrap = buildGreenButtonPopupContent(lat, lng, reverseGeocodeMarker, map);
      reverseGeocodeMarker.bindPopup(wrap, { className: 'team13-reverse-popup', closeButton: true }).openPopup();
      return;
    }
    if (!window.isPlacementMode) return;
    var map = getMap();
    if (!map || !e || !e.latlng) return;
    var lat = e.latlng.lat;
    var lng = e.latlng.lng;

    if (reverseGeocodeMarker && map) {
      map.removeLayer(reverseGeocodeMarker);
      reverseGeocodeMarker = null;
    }

    var markerIcon = L.divIcon({
      className: 'team13-reverse-marker',
      html: '<span style="width:22px;height:22px;background:#40916c;border:2px solid #1b4332;border-radius:50%;display:block;box-shadow:0 2px 8px rgba(0,0,0,0.3);"></span>',
      iconSize: [22, 22],
      iconAnchor: [11, 11],
    });
    reverseGeocodeMarker = L.marker([lat, lng], { icon: markerIcon }).addTo(map);

    function openPopupWithAddress(address) {
      var wrap = buildReversePopupContent(lat, lng, address, reverseGeocodeMarker, map);
      reverseGeocodeMarker.bindPopup(wrap, { className: 'team13-reverse-popup', closeButton: true }).openPopup();
      setPlacementModeActive(false);
    }

    if (window.Team13Api && typeof window.Team13Api.reverseGeocode === 'function') {
      window.Team13Api.reverseGeocode(lat, lng)
        .then(function (data) {
          var address = (data && (data.formatted_address || data.address || data.address_compact || data.postal_address)) || '';
          openPopupWithAddress(address || ('مختصات: ' + lat.toFixed(5) + ', ' + lng.toFixed(5)));
        })
        .catch(function () {
          openPopupWithAddress('آدرس یافت نشد');
        });
    } else {
      openPopupWithAddress('مختصات: ' + lat.toFixed(5) + ', ' + lng.toFixed(5));
    }
  }

  // --- لایو لوکیشن: فقط با کلیک دکمه (نقشه نشان map.locate ندارد؛ از Geolocation API استفاده می‌کنیم) ---
  var geoOptions = { enableHighAccuracy: true, timeout: 20000, maximumAge: 0 };

  function startUserLocationTracking() {
    // ردیابی خودکار غیرفعال؛ موقعیت با کلیک دکمه «موقعیت من» فعال می‌شود
  }

  function updateUserLocationOnMap(lat, lng) {
    var map = getMap();
    if (!map || !L) return;
    var latlng = { lat: lat, lng: lng };
    window.userLocationCoords = latlng;
    if (!window.userMarker) {
      window.userMarker = L.marker(latlng, {
        icon: createUserLocationIcon(),
        interactive: false,
        keyboard: false,
        zIndexOffset: 1000,
      }).addTo(map);
    } else {
      window.userMarker.setLatLng(latlng);
    }
    // همیشه نقشه را روی موقعیت فعلی کاربر مرکز و زوم کن (zoom 17 برای نمایش واضح)
    if (typeof map.flyTo === 'function') {
      map.flyTo(latlng, 17, { duration: 0.7 });
    }
    if (!window.userMarker || !window._userLocationWatchId) {
      if (window.showToast) window.showToast('موقعیت شما روی نقشه نمایش داده شد');
    }
  }

  function startLiveLocationWatch() {
    if (!navigator.geolocation || window._userLocationWatchId != null) return;
    window._userLocationWatchId = navigator.geolocation.watchPosition(
      function (pos) {
        updateUserLocationOnMap(pos.coords.latitude, pos.coords.longitude);
      },
      function (err) {
        var msg = 'موقعیت فعلی تشخیص داده نشد';
        if (err.code === 1) msg = 'دسترسی به موقعیت رد شد. در تنظیمات مرورگر اجازهٔ مکان را فعال کنید.';
        if (err.code === 2) msg = 'موقعیت در دسترس نیست. اتصال یا GPS را بررسی کنید.';
        if (err.code === 3) msg = 'زمان درخواست موقعیت تمام شد.';
        if (window.showToast) window.showToast(msg);
      },
      geoOptions
    );
  }

  /** نقشهٔ نشان (Mapbox): لایهٔ گروه addTo(map) ندارد؛ هر مارکر را جداگانه add/remove می‌کنیم. filter: 'all' | 'places' | 'events' | 'none' */
  function setPoiIconsVisible(visible, filter) {
    var f = filter !== undefined ? filter : (window._team13PoiFilter || 'all');
    if (f === 'none') visible = false;
    window._team13PoiFilter = f;
    window._team13PoiIconsVisible = !!visible;
    var map = getMap();
    if (!map || !L) return;
    var cityGroup = window.team13CityEventLayerGroup;
    var allMarkers = window.allMarkers || {};
    function showMarker(id, m) {
      if (m && typeof m.addTo === 'function' && !m._onMap) m.addTo(map);
    }
    function hideMarker(id, m) {
      if (m && (m._onMap || (map.hasLayer && map.hasLayer(m)))) {
        if (typeof m.remove === 'function') m.remove();
      }
    }
    function wantPlace(id) { return id.indexOf('place-') === 0; }
    function wantEvent(id) { return id.indexOf('event-') === 0; }
    if (!visible) {
      if (cityGroup && map.hasLayer && map.hasLayer(cityGroup)) map.removeLayer(cityGroup);
      Object.keys(allMarkers).forEach(function (id) { hideMarker(id, allMarkers[id]); });
    } else {
      if (f === 'all') {
        if (cityGroup && typeof cityGroup.addTo === 'function') cityGroup.addTo(map);
        Object.keys(allMarkers).forEach(function (id) { showMarker(id, allMarkers[id]); });
      } else if (f === 'places') {
        if (cityGroup && map.hasLayer && map.hasLayer(cityGroup)) map.removeLayer(cityGroup);
        var typeFilter = window._team13PlacesTypeFilter;
        var allowedTypes = (typeFilter && typeFilter.length) ? typeFilter : null;
        Object.keys(allMarkers).forEach(function (id) {
          if (!wantPlace(id)) { hideMarker(id, allMarkers[id]); return; }
          var m = allMarkers[id];
          if (allowedTypes && m && m._placeType != null) {
            var ok = allowedTypes.indexOf(m._placeType) !== -1;
            if (ok) showMarker(id, m); else hideMarker(id, m);
          } else {
            showMarker(id, m);
          }
        });
      } else if (f === 'events') {
        if (cityGroup && typeof cityGroup.addTo === 'function') cityGroup.addTo(map);
        Object.keys(allMarkers).forEach(function (id) {
          if (wantEvent(id)) showMarker(id, allMarkers[id]); else hideMarker(id, allMarkers[id]);
        });
      }
    }
  }

  function initPoiToggleButton() {
    var btn = document.getElementById('team13-btn-poi-toggle');
    if (!btn) return;
    function updateButtonState() {
      var on = window._team13PoiIconsVisible;
      btn.classList.toggle('team13-btn-poi-toggle-on', on);
      btn.classList.toggle('team13-btn-poi-toggle-off', !on);
      btn.setAttribute('aria-label', on ? 'فیلتر آیکون‌های نقشه' : 'نمایش آیکون مکان‌ها');
      btn.title = on ? 'تغییر فیلتر آیکون‌های مکان و رویداد' : 'نمایش آیکون مکان‌ها و رویدادها';
    }
    updateButtonState();
    window._team13UpdatePoiButtonState = updateButtonState;
    btn.addEventListener('click', function () {
      var map = getMap();
      if (map && L) {
        var allMarkers = window.allMarkers || {};
        var hasMarkers = Object.keys(allMarkers).length > 0;
        if (!hasMarkers && (window._team13PlacesCache || window._team13EventsCache)) {
          addPlaceMarkers(map, window._team13PlacesCache || []);
          addEventMarkers(map, window._team13EventsCache || []);
        }
      }
      if (typeof window.team13ShowModal === 'function') {
        window.team13ShowModal('team13-modal-poi-filter');
      }
    });
  }

  window.Team13ApplyPoiFilter = function (value) {
    if (value === 'none') {
      window._team13PoiFilter = 'none';
      window._team13PoiIconsVisible = false;
    } else {
      window._team13PoiFilter = value;
      window._team13PoiIconsVisible = true;
    }
    setPoiIconsVisible(window._team13PoiIconsVisible, value);
    savePoiFilterState();
    if (typeof window._team13UpdatePoiButtonState === 'function') window._team13UpdatePoiButtonState();
  };

  function buildPlaceTypeCheckboxesOnce() {
    var container = document.getElementById('team13-place-type-checkboxes');
    if (!container || container.querySelector('.team13-place-type-check-item')) return;
    PLACE_TYPES_FOR_FILTER.forEach(function (item) {
      var label = document.createElement('label');
      label.className = 'team13-place-type-label team13-place-type-check-item';
      label.innerHTML = '<input type="checkbox" class="team13-place-type-check team13-place-type-check-one" data-place-type="' + escapeHtml(item.key) + '"> <span>' + escapeHtml(item.label) + '</span>';
      container.appendChild(label);
    });
  }

  window.Team13ShowPlaceTypesModal = function () {
    buildPlaceTypeCheckboxesOnce();
    var checkAll = document.getElementById('team13-place-type-check-all');
    var container = document.getElementById('team13-place-type-checkboxes');
    var typeFilter = window._team13PlacesTypeFilter;
    var selectAll = !typeFilter || typeFilter.length === 0;
    if (checkAll) checkAll.checked = selectAll;
    if (container) {
      container.querySelectorAll('.team13-place-type-check-one').forEach(function (cb) {
        var key = cb.getAttribute('data-place-type');
        cb.checked = selectAll || (typeFilter && typeFilter.indexOf(key) !== -1);
        cb.disabled = !!selectAll && checkAll && checkAll.checked;
      });
    }
    if (checkAll && container) {
      checkAll.onchange = function () {
        var allChecked = checkAll.checked;
        container.querySelectorAll('.team13-place-type-check-one').forEach(function (cb) {
          cb.checked = allChecked;
          cb.disabled = allChecked;
        });
      };
    }
    if (container) {
      container.querySelectorAll('.team13-place-type-check-one').forEach(function (cb) {
        cb.onchange = function () {
          if (!checkAll) return;
          var anyUnchecked = false;
          container.querySelectorAll('.team13-place-type-check-one').forEach(function (c) { if (!c.disabled && !c.checked) anyUnchecked = true; });
          if (anyUnchecked) checkAll.checked = false;
          var allChecked = true;
          container.querySelectorAll('.team13-place-type-check-one').forEach(function (c) { if (!c.disabled && !c.checked) allChecked = false; });
          if (allChecked) checkAll.checked = true;
        };
      });
    }
    if (typeof window.team13ShowModal === 'function') window.team13ShowModal('team13-modal-place-types');
  };

  window.Team13ApplyPlaceTypesFilter = function () {
    var checkAll = document.getElementById('team13-place-type-check-all');
    var container = document.getElementById('team13-place-type-checkboxes');
    var selectAll = checkAll && checkAll.checked;
    if (selectAll) {
      window._team13PlacesTypeFilter = null;
    } else if (container) {
      var selected = [];
      container.querySelectorAll('.team13-place-type-check-one:checked').forEach(function (cb) {
        var k = cb.getAttribute('data-place-type');
        if (k) selected.push(k);
      });
      window._team13PlacesTypeFilter = selected.length ? selected : null;
    }
    window._team13PoiFilter = 'places';
    window._team13PoiIconsVisible = true;
    setPoiIconsVisible(true, 'places');
    savePoiFilterState();
    if (typeof window._team13UpdatePoiButtonState === 'function') window._team13UpdatePoiButtonState();
    if (typeof window.team13HideModal === 'function') window.team13HideModal('team13-modal-place-types');
  };

  function initPlaceTypesModalButton() {
    var applyBtn = document.getElementById('team13-place-types-apply');
    if (applyBtn) applyBtn.addEventListener('click', function () { if (typeof window.Team13ApplyPlaceTypesFilter === 'function') window.Team13ApplyPlaceTypesFilter(); });
  }

  function initAddPointerButton() {
    var btn = document.getElementById('team13-btn-add-pointer');
    if (!btn) return;
    btn.addEventListener('click', function () {
      if (window.isPlacementMode) {
        setPlacementModeActive(false);
      } else {
        setPlacementModeActive(true);
      }
    });
  }

  function initCenterOnMeButton() {
    var btn = document.getElementById('team13-btn-center-me');
    if (!btn) return;
    btn.addEventListener('click', function () {
      var map = getMap();
      if (!map) return;
      if (!navigator.geolocation) {
        if (window.showToast) window.showToast('مرورگر شما موقعیت مکانی را پشتیبانی نمی‌کند.');
        return;
      }
      // اگر قبلاً موقعیت داریم، بلافاصله نقشه را روی آن ببر و یک بار هم موقعیت تازه بگیر
      if (window.userLocationCoords && typeof map.flyTo === 'function') {
        map.flyTo(window.userLocationCoords, 17, { duration: 0.6 });
      }
      btn.disabled = true;
      navigator.geolocation.getCurrentPosition(
        function (pos) {
          var lat = pos.coords.latitude;
          var lng = pos.coords.longitude;
          updateUserLocationOnMap(lat, lng);
          startLiveLocationWatch();
          btn.disabled = false;
        },
        function (err) {
          btn.disabled = false;
          var msg = 'موقعیت فعلی تشخیص داده نشد';
          if (err.code === 1) msg = 'دسترسی به موقعیت رد شد. در تنظیمات مرورگر اجازهٔ مکان را فعال کنید.';
          if (err.code === 2) msg = 'موقعیت در دسترس نیست. اتصال یا GPS را بررسی کنید.';
          if (err.code === 3) msg = 'زمان درخواست موقعیت تمام شد. دوباره تلاش کنید.';
          if (window.showToast) window.showToast(msg);
        },
        geoOptions
      );
    });
  }

  // --- Discovery (اطراف من): radius-based POI search ---
  var discoveryCenter = null;
  var discoveryRadiusKm = 2;
  var discoveryCircleLayer = null;
  /** Single layer group for discovery POIs — created once, use clearLayers() to avoid removing base map. */
  var discoveryMarkersLayer = null;
  var pickModeDiscovery = false;

  /** Ensure discovery markers layer exists and is on the map once (recovery: never use map.eachLayer). */
  function ensureDiscoveryMarkersLayer() {
    var map = getMap();
    if (!map || !L) return null;
    if (!discoveryMarkersLayer) {
      discoveryMarkersLayer = L.layerGroup();
      discoveryMarkersLayer.addTo(map);
    }
    return discoveryMarkersLayer;
  }

  function distanceMeters(lat1, lng1, lat2, lng2) {
    var R = 6371000;
    var dLat = ((lat2 - lat1) * Math.PI) / 180;
    var dLng = ((lng2 - lng1) * Math.PI) / 180;
    var a = Math.sin(dLat / 2) * Math.sin(dLat / 2) +
      Math.cos((lat1 * Math.PI) / 180) * Math.cos((lat2 * Math.PI) / 180) * Math.sin(dLng / 2) * Math.sin(dLng / 2);
    var c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
    return R * c;
  }

  function buildDiscoveryPlacePopup(p, lat, lng) {
    var name = (p.name_fa || p.name_en || p.type_display || '').trim() || p.place_id;
    var address = (p.address || p.city || '').trim() || '—';
    var placeId = (p.place_id || p.id || '').toString();
    var base = (window.TEAM13_API_BASE || '/team13').replace(/\/$/, '');
    var detailUrl = base + '/places/' + (placeId || '') + '/';
    var btnDetails = '<button type="button" class="team13-btn-place-details team13-popup-btn-details" data-place-id="' + escapeHtml(placeId) + '" data-lat="' + lat + '" data-lng="' + lng + '" data-name="' + escapeHtml(name) + '">جزئیات (امتیاز / نظر / عکس)</button>';
    var html = '<div class="team13-popup team13-discovery-popup">' +
      '<strong>' + escapeHtml(name) + '</strong><br><span class="text-muted">' + escapeHtml(address) + '</span><br>' +
      btnDetails + ' <a href="' + escapeHtml(detailUrl) + '" class="team13-btn-discovery-detail">صفحهٔ جزئیات</a> ' +
      '<button type="button" class="team13-btn-discovery-route" data-lat="' + lat + '" data-lng="' + lng + '" data-place-id="' + escapeHtml(placeId) + '" data-name="' + escapeHtml(name) + '">مسیریابی به اینجا</button>' +
      '</div>';
    return html;
  }

  function switchToRoutesTabAndSetRoute(fromLat, fromLng, toLat, toLng, toName, mode) {
    var tabBtn = document.querySelector('[data-tab="routes"]');
    if (tabBtn) tabBtn.click();
    setStartFromCoords(fromLat, fromLng, '');
    setDestFromCoords(toLat, toLng, toName || '');
    routeMode = mode || 'driving';
    var modeWrap = document.getElementById('team13-route-mode-wrap');
    if (modeWrap) {
      modeWrap.querySelectorAll('.team13-route-mode-btn').forEach(function (b) {
        var isActive = (b.getAttribute('data-mode') || '') === routeMode;
        b.classList.toggle('active', isActive);
        b.classList.toggle('active-transport', isActive);
      });
    }
    drawRouteFromToIfBoth();
  }

  /** Deselect Area: remove circle, clear POI markers via clearLayers() (do not remove layer group), reset radius, clear center, deactivate Pick on Map. */
  function clearDiscoveryArea() {
    var map = getMap();
    if (discoveryCircleLayer && map && map.hasLayer(discoveryCircleLayer)) {
      map.removeLayer(discoveryCircleLayer);
      discoveryCircleLayer = null;
    }
    if (discoveryMarkersLayer) {
      discoveryMarkersLayer.clearLayers();
    }
    discoveryCenter = null;
    discoveryRadiusKm = 0.5;
    pickModeDiscovery = false;
    updateSelectionActiveCursor();
    var btnPick = document.getElementById('team13-discovery-pick-map');
    if (btnPick) btnPick.classList.remove('active');
    var slider = document.getElementById('team13-discovery-radius');
    var valueEl = document.getElementById('team13-discovery-radius-value');
    if (slider) {
      slider.value = 0.5;
      discoveryRadiusKm = 0.5;
    }
    if (valueEl) valueEl.textContent = '0.5';
    updateSidebarResults([]);
    if (window.showToast) window.showToast('محدوده پاکسازی شد');
  }

  function runDiscoverySearch() {
    var map = getMap();
    if (!map) return;
    if (!discoveryCenter) {
      if (window.showToast) window.showToast('ابتدا نقطه مرکز را انتخاب کنید.');
      return;
    }
    if (window.currentlyShownPoiMarker && map.hasLayer(window.currentlyShownPoiMarker)) {
      map.removeLayer(window.currentlyShownPoiMarker);
      window.currentlyShownPoiMarker = null;
    }
    if (searchResultMarker && map.hasLayer(searchResultMarker)) {
      map.removeLayer(searchResultMarker);
      searchResultMarker = null;
    }
    if (window.emergencyPoiMarker && map.hasLayer(window.emergencyPoiMarker)) {
      map.removeLayer(window.emergencyPoiMarker);
      window.emergencyPoiMarker = null;
    }
    if (reverseGeocodeMarker && map.hasLayer(reverseGeocodeMarker)) {
      map.removeLayer(reverseGeocodeMarker);
      reverseGeocodeMarker = null;
    }
    var checked = document.querySelectorAll('input[name="discovery-cat"]:checked');
    var selectedTypes = [];
    checked.forEach(function (el) { selectedTypes.push(el.value); });
    var radiusM = discoveryRadiusKm * 1000;
    var centerLat = discoveryCenter.lat;
    var centerLng = discoveryCenter.lng;

    var API_BASE = (window.TEAM13_API_BASE || '/team13').replace(/\/$/, '');
    var url = API_BASE + '/places-in-radius/?lat=' + encodeURIComponent(centerLat) + '&lng=' + encodeURIComponent(centerLng) + '&radius_km=' + encodeURIComponent(discoveryRadiusKm) + '&limit=2000';
    if (selectedTypes.length > 0) url += '&type=' + encodeURIComponent(selectedTypes.join(','));

    if (window.showToast) window.showToast('در حال جستجو در دیتابیس…');
    fetch(url, { method: 'GET', headers: { Accept: 'application/json' }, credentials: 'same-origin' })
      .then(function (res) {
        if (!res.ok) return Promise.reject(new Error('خطا در دریافت مکان‌ها: ' + res.status));
        return res.json().catch(function () { return Promise.reject(new Error('پاسخ نامعتبر')); });
      })
      .then(function (data) {
        var filtered = Array.isArray(data && data.places) ? data.places : [];
        applyDiscoveryResults(map, centerLat, centerLng, radiusM, filtered);
      })
      .catch(function (err) {
        if (window.showToast) window.showToast('بارگذاری مکان‌های محدوده ناموفق بود.');
        applyDiscoveryResults(map, centerLat, centerLng, radiusM, []);
      });
  }

  function applyDiscoveryResults(map, centerLat, centerLng, radiusM, filtered) {
    if (discoveryCircleLayer && map) map.removeLayer(discoveryCircleLayer);
    discoveryCircleLayer = L.circle([centerLat, centerLng], {
      radius: radiusM,
      color: '#40916c',
      fillColor: '#40916c',
      fillOpacity: 0.12,
      weight: 2,
    }).addTo(map);

    var layer = ensureDiscoveryMarkersLayer();
    if (layer) layer.clearLayers();
    (filtered || []).forEach(function (p) {
      var lat = parseFloat(p.latitude || p.lat);
      var lng = parseFloat(p.longitude || p.lng);
      if (isNaN(lat) || isNaN(lng)) return;
      var popupContent = buildDiscoveryPlacePopup(p, lat, lng);
      var discoveryIcon = p.is_user_contributed ? createDiscoveryUserContributedIcon() : createDiscoveryPlaceIcon(p.type || p.category);
      var m = L.marker([lat, lng], { icon: discoveryIcon }).bindPopup(popupContent);
      m._team13DiscoveryPlace = p;
      if (discoveryMarkersLayer) discoveryMarkersLayer.addLayer(m);
      if (map && typeof m.addTo === 'function') m.addTo(map);
    });

    if (discoveryMarkersLayer) discoveryMarkersLayer.eachLayer(function (layer) {
      if (layer.bindPopup && layer.getPopup) {
        layer.on('popupopen', function () {
          var popup = layer.getPopup();
          var el = popup && popup.getElement && popup.getElement();
          if (!el) return;
          var btn = el.querySelector('.team13-btn-discovery-route');
          if (!btn || btn._bound) return;
          btn._bound = true;
          btn.addEventListener('click', function () {
            var lat = parseFloat(btn.getAttribute('data-lat'));
            var lng = parseFloat(btn.getAttribute('data-lng'));
            var name = btn.getAttribute('data-name') || '';
            if (!discoveryCenter || isNaN(lat) || isNaN(lng)) return;
            var wrap = document.createElement('div');
            wrap.className = 'team13-discovery-route-mode';
            wrap.innerHTML = '<p class="team13-discovery-route-title">نوع مسیر:</p>' +
              '<button type="button" class="team13-route-mode-btn" data-mode="driving">خودرو</button>' +
              '<button type="button" class="team13-route-mode-btn" data-mode="walking">پیاده</button>' +
              '<button type="button" class="team13-route-mode-btn" data-mode="bicycle">دوچرخه</button>';
            var btns = wrap.querySelectorAll('.team13-route-mode-btn');
            btns.forEach(function (b) {
              b.addEventListener('click', function () {
                var mode = b.getAttribute('data-mode') || 'driving';
                switchToRoutesTabAndSetRoute(discoveryCenter.lat, discoveryCenter.lng, lat, lng, name, mode);
              });
            });
            popup.setContent(wrap);
          });
        });
      }
    });

    if (filtered.length > 0 && discoveryMarkersLayer) map.fitBounds(discoveryMarkersLayer.getBounds(), { padding: [40, 40], maxZoom: 15 });
    if (window.showToast) window.showToast('یافت شد: ' + filtered.length + ' مکان — روی نقشه و در لیست سمت راست نمایش داده شدند.');
    var sidebarItems = filtered.map(function (p) {
      var name = (p.name_fa || p.name_en || p.type_display || '').trim() || (p.type || 'مکان');
      return {
        title: name,
        address: p.address || p.city || name,
        lat: parseFloat(p.latitude),
        lng: parseFloat(p.longitude),
        latitude: parseFloat(p.latitude),
        longitude: parseFloat(p.longitude),
        y: parseFloat(p.latitude),
        x: parseFloat(p.longitude),
      };
    });
    updateSidebarResults(sidebarItems, 'مکان‌های این محدوده');
    var sidebarWrap = document.getElementById('team13-sidebar-search-results-wrap');
    if (sidebarWrap && typeof window.Team13OpenSidebar === 'function') window.Team13OpenSidebar();
  }

  function initDiscoveryUI() {
    var map = getMap();
    if (map) ensureDiscoveryMarkersLayer();
    var btnMyLoc = document.getElementById('team13-discovery-my-location');
    var btnPick = document.getElementById('team13-discovery-pick-map');
    var slider = document.getElementById('team13-discovery-radius');
    var valueEl = document.getElementById('team13-discovery-radius-value');
    var btnSearch = document.getElementById('team13-discovery-search');

    if (btnMyLoc) {
      btnMyLoc.addEventListener('click', function () {
        if (!navigator.geolocation) {
          if (window.showToast) window.showToast('موقعیت یافت نشد');
          return;
        }
        navigator.geolocation.getCurrentPosition(
          function (pos) {
            discoveryCenter = { lat: pos.coords.latitude, lng: pos.coords.longitude };
            pickModeDiscovery = false;
            updateSelectionActiveCursor();
            if (btnPick) btnPick.classList.remove('active');
            var radiusKm = parseFloat(slider && slider.value) || 2;
            discoveryRadiusKm = radiusKm;
            if (discoveryCircleLayer && map) map.removeLayer(discoveryCircleLayer);
            discoveryCircleLayer = L.circle([discoveryCenter.lat, discoveryCenter.lng], {
              radius: radiusKm * 1000,
              color: '#40916c',
              fillColor: '#40916c',
              fillOpacity: 0.12,
              weight: 2,
            }).addTo(map);
            flyTo(map, discoveryCenter.lat, discoveryCenter.lng, 14);
            if (window.showToast) window.showToast('مرکز روی موقعیت شما تنظیم شد');
          },
          function () {
            if (window.showToast) window.showToast('دسترسی به موقعیت امکان‌پذیر نیست');
          },
          { enableHighAccuracy: true, timeout: 10000, maximumAge: 60000 }
        );
      });
    }

    if (btnPick) {
      btnPick.addEventListener('click', function () {
        pickModeDiscovery = !pickModeDiscovery;
        updateSelectionActiveCursor();
        btnPick.classList.toggle('active', pickModeDiscovery);
      });
    }

    if (slider && valueEl) {
      slider.addEventListener('input', function () {
        discoveryRadiusKm = parseFloat(slider.value) || 2;
        valueEl.textContent = discoveryRadiusKm;
      });
      valueEl.textContent = parseFloat(slider.value) || 2;
    }

    if (btnSearch) btnSearch.addEventListener('click', runDiscoverySearch);
    var btnClearArea = document.getElementById('team13-discovery-clear-area');
    if (btnClearArea) btnClearArea.addEventListener('click', clearDiscoveryArea);
    var btnDeselect = document.getElementById('team13-discovery-deselect');
    if (btnDeselect) btnDeselect.addEventListener('click', clearDiscoveryArea);
  }

  function onMapClickForDiscovery(e) {
    if (!pickModeDiscovery) return false;
    var map = getMap();
    if (!map || !e || !e.latlng) return true;
    var lat = e.latlng.lat;
    var lng = e.latlng.lng;
    pickModeDiscovery = false;
    updateSelectionActiveCursor();
    var btnPick = document.getElementById('team13-discovery-pick-map');
    if (btnPick) btnPick.classList.remove('active');
    discoveryCenter = { lat: lat, lng: lng };
    var radiusKm = parseFloat(document.getElementById('team13-discovery-radius') && document.getElementById('team13-discovery-radius').value) || 2;
    discoveryRadiusKm = radiusKm;
    if (discoveryCircleLayer && map) map.removeLayer(discoveryCircleLayer);
    discoveryCircleLayer = L.circle([lat, lng], {
      radius: radiusKm * 1000,
      color: '#40916c',
      fillColor: '#40916c',
      fillOpacity: 0.12,
      weight: 2,
    }).addTo(map);
    if (window.showToast) window.showToast('مرکز انتخاب شد');
    return true;
  }

  // --- Events tab: city selector + Events Near Me ---
  function initEventsCityUI() {
    var cityInput = document.getElementById('team13-events-city-input');
    var btnNearMe = document.getElementById('team13-events-near-me');

    if (btnNearMe) {
      btnNearMe.addEventListener('click', function () {
        if (!window.Team13Api || typeof window.Team13Api.getCityFromCoords !== 'function') {
          if (window.showToast) window.showToast('سرویس موقعیت در دسترس نیست');
          return;
        }
        if (!navigator.geolocation) {
          if (window.showToast) window.showToast('دسترسی به موقعیت امکان‌پذیر نیست');
          return;
        }
        if (window.showToast) window.showToast('در حال دریافت موقعیت...');
        navigator.geolocation.getCurrentPosition(
          function (pos) {
            var lat = pos.coords.latitude;
            var lng = pos.coords.longitude;
            window.Team13Api.getCityFromCoords(lat, lng).then(function (result) {
              if (!result || !result.city) {
                if (window.showToast) window.showToast('شهر برای این موقعیت یافت نشد');
                return;
              }
              if (cityInput) cityInput.value = result.city;
              applyEventCityFilter(result.city, result.lat, result.lng);
              if (window.showToast) window.showToast('رویدادهای ' + result.city);
            }).catch(function () {
              if (window.showToast) window.showToast('خطا در دریافت شهر');
            });
          },
          function () {
            if (window.showToast) window.showToast('دسترسی به موقعیت امکان‌پذیر نیست');
          },
          { enableHighAccuracy: true, timeout: 10000, maximumAge: 60000 }
        );
      });
    }

    if (cityInput) {
      function applyCityFromInput() {
        var city = (cityInput.value && cityInput.value.trim()) || '';
        if (city) window.currentCity = city;
        if (city && window.Team13Api && window.Team13Api.fetchData) {
          var base = (window.TEAM13_API_BASE || '/team13').replace(/\/$/, '');
          var url = base + '/events/?format=json&city=' + encodeURIComponent(city);
          if (window.showToast) window.showToast('در حال بارگذاری رویدادها از دیتابیس...');
          fetch(url, { method: 'GET', headers: { Accept: 'application/json' }, credentials: 'same-origin' })
            .then(function (res) { return res.json(); })
            .then(function (data) {
              var list = (data && data.events) ? data.events : [];
              window._team13EventsCache = list;
              applyEventCityFilter(city, null, null);
              if (window.showToast) window.showToast(list.length ? 'رویدادهای ' + city + ': ' + list.length : 'رویدادی برای این شهر در دیتابیس نیست');
            })
            .catch(function () {
              if (window.showToast) window.showToast('خطا در بارگذاری رویدادها');
              applyEventCityFilter(city || null, null, null);
            });
        } else {
          applyEventCityFilter(city || null, null, null);
        }
      }
      cityInput.addEventListener('change', applyCityFromInput);
      cityInput.addEventListener('keydown', function (e) {
        if (e.key === 'Enter') {
          e.preventDefault();
          applyCityFromInput();
        }
      });
    }
  }

  // --- Run: sync layers + init search + emergency + reverse geocode click + start/dest UI + live location + discovery + events city ---
  function run() {
    var map = getMap();
    if (!map) return;
    window.team13MapDataReady = function () {
      syncDatabaseLayers().catch(function (err) {
        console.warn('Team13 syncDatabaseLayers failed', err);
      });
    };
    syncDatabaseLayers().catch(function (err) {
      console.warn('Team13 syncDatabaseLayers failed', err);
    });
    initSearch();
    initEmergencyButtons();
    initStartDestUI();
    initDiscoveryUI();
    initEventsCityUI();
    initReverseGeocodeClick();
    startUserLocationTracking();
    initCenterOnMeButton();
    initPoiToggleButton();
    initPlaceTypesModalButton();
    initAddPointerButton();
  }

  function waitMapAndRun() {
    if (getMap() && window.Team13Api) {
      run();
      return;
    }
    setTimeout(waitMapAndRun, 150);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', waitMapAndRun);
  } else {
    waitMapAndRun();
  }

  function clearSearchResult() {
    var map = getMap();
    if (searchResultMarker && map) {
      map.removeLayer(searchResultMarker);
      searchResultMarker = null;
    }
    var input = document.getElementById('team13-search-input');
    if (input) input.value = '';
    var resultsEl = document.getElementById('team13-search-results');
    if (resultsEl) { resultsEl.hidden = true; resultsEl.innerHTML = ''; }
    var sidebarWrap = document.getElementById('team13-sidebar-search-results-wrap');
    var sidebarResultsEl = document.getElementById('team13-sidebar-search-results');
    if (sidebarWrap) sidebarWrap.hidden = true;
    if (sidebarResultsEl) sidebarResultsEl.innerHTML = '';
  }

  /** Called when user switches to Events tab: optional city detection and filter; smooth FlyTo on city change. */
  function onEventsTabActivated() {
    if (!window.Team13Api || typeof window.Team13Api.getCityFromCoords !== 'function') return;
    if (window._team13EventsCityAutoDone) return;
    if (!navigator.geolocation) return;
    window._team13EventsCityAutoDone = true;
    navigator.geolocation.getCurrentPosition(
      function (pos) {
        var lat = pos.coords.latitude;
        var lng = pos.coords.longitude;
        window.Team13Api.getCityFromCoords(lat, lng).then(function (result) {
          if (!result || !result.city) return;
          var cityInput = document.getElementById('team13-events-city-input');
          if (cityInput) cityInput.value = result.city;
          applyEventCityFilter(result.city, result.lat, result.lng);
          if (window.showToast) window.showToast('رویدادهای ' + result.city);
        }).catch(function () {});
      },
      function () {},
      { enableHighAccuracy: true, timeout: 8000, maximumAge: 120000 }
    );
  }

    function startMapPickForFavorite(callback) {
    window._team13PickForFavorite = callback;
  }

  window.Team13MapData = {
    syncDatabaseLayers: syncDatabaseLayers,
    startMapPickForFavorite: startMapPickForFavorite,
    mapirAutocomplete: typeof mapirAutocomplete !== 'undefined' ? mapirAutocomplete : function () { return Promise.resolve([]); },
    getItemLatLng: typeof getItemLatLng !== 'undefined' ? getItemLatLng : function () { return null; },
    getMap: getMap,
    getMapCenter: function () {
      var map = getMap();
      if (!map || !map.getCenter) return null;
      var c = map.getCenter();
      return c ? { lat: c.lat, lng: c.lng } : null;
    },
    getRouteToPlace: requestRouteFromUserTo,
    setStartFromCoords: typeof setStartFromCoords !== 'undefined' ? setStartFromCoords : function () {},
    setDestFromCoords: typeof setDestFromCoords !== 'undefined' ? setDestFromCoords : function () {},
    swapStartDest: typeof swapStartDest !== 'undefined' ? swapStartDest : function () {},
    setRouteMode: typeof setRouteMode !== 'undefined' ? setRouteMode : function () {},
    drawRouteFromToIfBoth: typeof drawRouteFromToIfBoth !== 'undefined' ? drawRouteFromToIfBoth : function () {},
    setPickMode: typeof setPickMode !== 'undefined' ? setPickMode : function () {},
    flyTo: flyTo,
    panTo: function (map, lat, lng) { flyTo(map, lat, lng); },
    showFavoritePickMarker: typeof showFavoritePickMarker !== 'undefined' ? showFavoritePickMarker : function () {},
    clearFavoritePickMarker: typeof clearFavoritePickMarker !== 'undefined' ? clearFavoritePickMarker : function () {},
    clearReverseGeocodeMarker: typeof clearReverseGeocodeMarker !== 'undefined' ? clearReverseGeocodeMarker : function () {},
    addPlaceMarkers: addPlaceMarkers,
    addEventMarkers: addEventMarkers,
    clearSearchResult: clearSearchResult,
    applyEventCityFilter: applyEventCityFilter,
    onEventsTabActivated: onEventsTabActivated,
    run: run,
  };
})();
