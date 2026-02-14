/**
 * Team 13 — راه‌اندازی نقشهٔ نشان و دکمه‌های مسیر/خانه/پاک‌کردن.
 * نقشه توسط neshan_map.js ساخته می‌شود؛ این فایل فقط setView و رویدادها را متصل می‌کند.
 */
(function () {
  window.MAPIR_CONFIG = { apiKey: '', routingUrl: '' };

  function escapeHtml(s) {
    if (!s) return '';
    var div = document.createElement('div');
    div.textContent = s;
    return div.innerHTML;
  }

  /**
   * Show a small toast notification (e.g. "زمان: ۱۲ دقیقه | فاصله: ۴.۵ کیلومتر").
   * @param {string} message
   */
  function showToast(message) {
    var container = document.getElementById('team13-toast');
    if (!container) {
      container = document.createElement('div');
      container.id = 'team13-toast';
      container.className = 'team13-toast';
      document.body.appendChild(container);
    }
    var el = document.createElement('div');
    el.className = 'team13-toast-item';
    el.textContent = message;
    container.appendChild(el);
    setTimeout(function () {
      if (el.parentNode) el.parentNode.removeChild(el);
    }, 4000);
  }

  /** Small SVG icons for route mode in #route-info-box (Car, Foot, Bicycle, Transit). */
  var iconCar = '<span class="team13-route-mode-icon team13-route-mode-car" title="سواره" aria-hidden="true"><svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor"><path d="M18.92 6.01C18.72 5.42 18.16 5 17.5 5h-11c-.66 0-1.21.42-1.42 1.01L3 12v8c0 .55.45 1 1 1h1c.55 0 1-.45 1-1v-1h12v1c0 .55.45 1 1 1h1c.55 0 1-.45 1-1v-8l-2.08-5.99zM6.5 16c-.83 0-1.5-.67-1.5-1.5S5.67 13 6.5 13s1.5.67 1.5 1.5S7.33 16 6.5 16zm11 0c-.83 0-1.5-.67-1.5-1.5s.67-1.5 1.5-1.5 1.5.67 1.5 1.5-.67 1.5-1.5 1.5zM5 11l1.5-4.5h11L19 11H5z"/></svg></span>';
  var iconPedestrian = '<span class="team13-route-mode-icon team13-route-mode-pedestrian" title="پیاده" aria-hidden="true"><svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor"><path d="M13.5 5.5c1.1 0 2-.9 2-2s-.9-2-2-2-2 .9-2 2 .9 2 2 2zM9.8 8.9L7 23h2.1l1.8-8 2.1 2v6h2v-7.5l-2.1-2 .6-3C14.8 12 16.8 13 19 13v-2c-1.9 0-3.5-1-4.3-2.4l-1-1.6c-.4-.6-1-1-1.7-1-.3 0-.5.1-.8.1L6 8.3V13h2V9.6l1.8-.7"/></svg></span>';
  var iconBicycle = '<span class="team13-route-mode-icon team13-route-mode-bicycle" title="دوچرخه" aria-hidden="true"><svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor"><path d="M15.5 5.5c1.1 0 2-.9 2-2s-.9-2-2-2-2 .9-2 2 .9 2 2 2zM5 12c-2.8 0-5 2.2-5 5s2.2 5 5 5 5-2.2 5-5-2.2-5-5-5zm0 8.5c-1.9 0-3.5-1.6-3.5-3.5s1.6-3.5 3.5-3.5 3.5 1.6 3.5 3.5-1.6 3.5-3.5 3.5zm5-8.5l1.5-3 1.5 2h3l-2.5-4-2.5 4zm5.5 0c-2.8 0-5 2.2-5 5s2.2 5 5 5 5-2.2 5-5-2.2-5-5-5zm0 8.5c-1.9 0-3.5-1.6-3.5-3.5s1.6-3.5 3.5-3.5 3.5 1.6 3.5 3.5-1.6 3.5-3.5 3.5z"/></svg></span>';
  var iconTransit = '<span class="team13-route-mode-icon team13-route-mode-transit" title="حمل‌ونقل عمومی" aria-hidden="true"><svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor"><path d="M4 16c0 .88.39 1.67 1 2.22V20c0 .55.45 1 1 1h1c.55 0 1-.45 1-1v-1h8v1c0 .55.45 1 1 1h1c.55 0 1-.45 1-1v-1.78c.61-.55 1-1.34 1-2.22V6c0-3.5-3.58-4-8-4s-8 .5-8 4v10zm3.5 1c-.83 0-1.5-.67-1.5-1.5S6.67 14 7.5 14s1.5.67 1.5 1.5S8.33 17 7.5 17zm9 0c-.83 0-1.5-.67-1.5-1.5s.67-1.5 1.5-1.5 1.5.67 1.5 1.5-.67 1.5-1.5 1.5zm1.5-6H6V6h12v5z"/></svg></span>';

  function getModeIcon(serviceType) {
    if (serviceType === 'walking') return iconPedestrian;
    if (serviceType === 'bicycle') return iconBicycle;
    if (serviceType === 'transit') return iconTransit;
    return iconCar;
  }

  /**
   * Update sidebar #route-info-box with ETA, distance and correct mode icon (Car, Foot, Bicycle, Transit).
   * @param {{ distanceKm: number|null, durationMinutes: number|null, serviceType: string }} r
   */
  function updateRouteInfoBox(r) {
    var content = document.getElementById('route-info-box-content');
    var clearWrap = document.getElementById('team13-clear-route-wrap');
    var clearBtn = document.getElementById('team13-btn-clear-path');
    if (!content) return;
    if (r && (r.durationMinutes != null || r.distanceKm != null)) {
      var timeStr = r.durationMinutes != null ? (toPersianNum(r.durationMinutes) + ' دقیقه') : '—';
      var distStr = r.distanceKm != null ? (toPersianNum(Math.round(r.distanceKm * 10) / 10) + ' کیلومتر') : '—';
      var modeIcon = getModeIcon(r.serviceType);
      content.innerHTML = '<p class="team13-route-info-row">' + modeIcon + ' <strong>زمان تخمینی:</strong> ' + timeStr + '</p><p><strong>فاصله:</strong> ' + distStr + '</p>';
      if (clearWrap) clearWrap.style.display = '';
      else if (clearBtn) clearBtn.style.display = 'block';
    } else {
      content.textContent = 'مسیری را از نقشه یا جستجو انتخاب کنید.';
      if (clearWrap) clearWrap.style.display = 'none';
      else if (clearBtn) clearBtn.style.display = 'none';
    }
  }

  /** Convert Western digits to Persian (۰-۹). */
  function toPersianNum(n) {
    if (n == null || isNaN(n)) return '';
    var s = String(n);
    var persian = '\u06F0\u06F1\u06F2\u06F3\u06F4\u06F5\u06F6\u06F7\u06F8\u06F9';
    return s.replace(/\d/g, function (d) { return persian[parseInt(d, 10)]; });
  }

  /**
   * نمایش پاپ‌آپ اکشن در (lat, lng): مسیریابی سواره، پیاده، دوچرخه، حمل‌ونقل عمومی.
   */
  function showActionMenu(lat, lng, title) {
    var map = window.team13MapInstance;
    if (!map || typeof L === 'undefined') return;

    var wrap = document.createElement('div');
    wrap.className = 'team13-action-menu';
    wrap.innerHTML =
      '<p class="team13-action-menu-title">' + escapeHtml(title || 'مکان') + '</p>' +
      '<div class="team13-action-menu-btns">' +
      '<button type="button" class="team13-action-btn-driving">خودرو</button>' +
      '<button type="button" class="team13-action-btn-walking">پیاده</button>' +
      '<button type="button" class="team13-action-btn-bicycle">دوچرخه</button>' +
      '<button type="button" class="team13-action-btn-transit">حمل و نقل</button>' +
      '<div class="team13-action-menu-eta" id="team13-popup-eta-placeholder">فاصله و زمان — پس از انتخاب مسیر نمایش داده می‌شود.</div>' +
      '</div>';

    var btnDriving = wrap.querySelector('.team13-action-btn-driving');
    var btnWalking = wrap.querySelector('.team13-action-btn-walking');
    var btnBicycle = wrap.querySelector('.team13-action-btn-bicycle');
    var btnTransit = wrap.querySelector('.team13-action-btn-transit');
    var etaPlaceholder = wrap.querySelector('#team13-popup-eta-placeholder');

    [btnDriving, btnWalking, btnBicycle, btnTransit].forEach(function (btn) {
      if (btn) L.DomEvent.on(btn, 'click', L.DomEvent.stopPropagation);
    });

    function runRoute(serviceType) {
      if (!window.Team13Api || typeof window.Team13Api.getRouteFromUserToPoint !== 'function') return;
      if (etaPlaceholder) etaPlaceholder.textContent = 'در حال بارگذاری...';
      window.Team13Api.getRouteFromUserToPoint({ lat: lat, lng: lng }, serviceType)
        .then(function (r) {
          if (etaPlaceholder && r && (r.durationMinutes != null || r.distanceKm != null)) {
            var timeStr = r.durationMinutes != null ? (toPersianNum(r.durationMinutes) + ' دقیقه') : '—';
            var distStr = r.distanceKm != null ? (toPersianNum(Math.round(r.distanceKm * 10) / 10) + ' کیلومتر') : '—';
            etaPlaceholder.innerHTML = '<strong>زمان تخمینی:</strong> ' + timeStr + ' | <strong>فاصله:</strong> ' + distStr;
          } else if (etaPlaceholder) {
            etaPlaceholder.textContent = 'اطلاعات مسیر در دسترس نیست.';
          }
          if (typeof window.updateRouteInfoBox === 'function') window.updateRouteInfoBox(r);
        })
        .catch(function (err) {
          if (etaPlaceholder) etaPlaceholder.textContent = 'خطا: ' + (err && err.message ? err.message : 'مسیریابی ناموفق');
          showToast('خطا: ' + (err && err.message ? err.message : 'مسیریابی ناموفق'));
        });
    }

    L.DomEvent.on(btnDriving, 'click', function () { runRoute('driving'); });
    L.DomEvent.on(btnWalking, 'click', function () { runRoute('walking'); });
    L.DomEvent.on(btnBicycle, 'click', function () { runRoute('bicycle'); });
    L.DomEvent.on(btnTransit, 'click', function () { runRoute('transit'); });

    L.popup({ className: 'team13-action-popup' })
      .setLatLng([lat, lng])
      .setContent(wrap)
      .openOn(map);
  }

  /**
   * Home action: redirect to site root (stays on same origin; use 127.0.0.1:8000 for local).
   */
  function goHome() {
    window.location.href = 'http://127.0.0.1:8000';
  }

  function initHomeButton() {
    var btn = document.getElementById('team13-btn-home');
    if (!btn) return;
    L.DomEvent.on(btn, 'click', goHome);
  }

  function initMap() {
    if (typeof L === 'undefined') return;
    var map = window.team13MapInstance;
    if (!map) return;
    map.setView([35.7219, 51.3347], 12);
    setTimeout(function () {
      if (map && typeof map.invalidateSize === 'function') map.invalidateSize();
    }, 500);
  }

  function initClearPathButton() {
    var btn = document.getElementById('team13-btn-clear-path');
    var wrap = document.getElementById('team13-clear-route-wrap');
    if (!btn) return;
    L.DomEvent.on(btn, 'click', function () {
      var map = window.team13MapInstance;
      var routeLayer = window.currentPath || window.routeLayer || window.currentRoute || window.team13RouteLine;
      if (routeLayer && map) {
        map.removeLayer(routeLayer);
      }
      window.currentPath = null;
      window.routeLayer = null;
      window.currentRoute = null;
      window.team13RouteLine = null;
      updateRouteInfoBox(null);
      if (wrap) wrap.style.display = 'none';
      else if (btn) btn.style.display = 'none';
      if (map) map.setView([35.7219, 51.3347], 12);
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function () {
      initMap();
      initClearPathButton();
      initHomeButton();
    });
  } else {
    initMap();
    initClearPathButton();
    initHomeButton();
  }

  window.showActionMenu = showActionMenu;
  window.showToast = showToast;
  window.updateRouteInfoBox = updateRouteInfoBox;
  window.toPersianNum = toPersianNum;
  window.goHome = goHome;
})();
