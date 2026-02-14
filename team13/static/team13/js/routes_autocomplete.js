/**
 * Team 13 — صفحهٔ مسیریابی (مبدأ/مقصد). جستجو فقط از دیتابیس خودمان (SQLite).
 */
(function () {
  var base = (window.TEAM13_API_BASE || '/team13').replace(/\/$/, '');
  var SEARCH_PLACES_URL = base + '/search-places/';

  function searchPlacesAutocomplete(text) {
    if (!(text && text.trim())) return Promise.resolve([]);
    var url = SEARCH_PLACES_URL + '?q=' + encodeURIComponent(text.trim()) + '&limit=20';
    return fetch(url, { method: 'GET', headers: { Accept: 'application/json' }, credentials: 'same-origin' })
      .then(function (res) { return res.ok ? res.json() : { items: [] }; })
      .then(function (data) { return (data && data.items) ? data.items : []; })
      .catch(function () { return []; });
  }

  function getItemLatLng(item) {
    if (item.lat != null && item.lng != null) return { lat: parseFloat(item.lat), lng: parseFloat(item.lng) };
    if (item.y != null && item.x != null) return { lat: parseFloat(item.y), lng: parseFloat(item.x) };
    if (item.y != null && item.x != null) return { lat: parseFloat(item.y), lng: parseFloat(item.x) };
    if (item.latitude != null && item.longitude != null) return { lat: parseFloat(item.latitude), lng: parseFloat(item.longitude) };
    var geom = item.geom || item.geometry;
    if (geom && geom.coordinates && Array.isArray(geom.coordinates) && geom.coordinates.length >= 2)
      return { lng: parseFloat(geom.coordinates[0]), lat: parseFloat(geom.coordinates[1]) };
    return null;
  }

  function bindAutocomplete(inputEl, resultsEl, setLat, setLng, setName) {
    if (!inputEl || !resultsEl) return;
    var debounce;
    inputEl.addEventListener('input', function () {
      clearTimeout(debounce);
      var q = (inputEl.value || '').trim();
      if (q.length < 2) { resultsEl.hidden = true; resultsEl.innerHTML = ''; return; }
      debounce = setTimeout(function () {
        searchPlacesAutocomplete(q).then(function (items) {
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
              inputEl.value = title;
              if (setLat) setLat.value = ll.lat;
              if (setLng) setLng.value = ll.lng;
              if (setName) setName.value = title;
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

  function init() {

    var sourceInput = document.getElementById('routes_source_search');
    var sourceResults = document.getElementById('routes_source_results');
    var destInput = document.getElementById('routes_dest_search');
    var destResults = document.getElementById('routes_dest_results');
    var sourceLat = document.getElementById('source_lat');
    var sourceLng = document.getElementById('source_lng');
    var sourceName = document.getElementById('source_name');
    var destLat = document.getElementById('dest_lat');
    var destLng = document.getElementById('dest_lng');
    var destName = document.getElementById('dest_name');

    bindAutocomplete(sourceInput, sourceResults, sourceLat, sourceLng, sourceName);
    bindAutocomplete(destInput, destResults, destLat, destLng, destName);

    var form = document.getElementById('team13-routes-form');
    if (form) {
      form.addEventListener('submit', function (e) {
        if (!sourceLat || !sourceLng || !sourceLat.value || !sourceLng.value) {
          e.preventDefault();
          if (sourceInput) sourceInput.focus();
          return;
        }
        if (!destLat || !destLng || !destLat.value || !destLng.value) {
          e.preventDefault();
          if (destInput) destInput.focus();
          return;
        }
      });
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
