/**
 * Team 13 — نقشهٔ نشان با Mapbox GL JS SDK
 * مستندات: https://platform.neshan.org/docs/sdk/web/mapboxgl/neshan-mapbox-gl-js/
 * مارکر: https://platform.neshan.org/docs/sdk/web/mapboxgl/examples/neshan-mapbox-add-marker/
 * رسم مسیر: https://platform.neshan.org/docs/sdk/web/mapboxgl/examples/neshan-mapbox-draw-route/
 * نقشه با nmp_mapboxgl.Map؛ مسیر با L.polyline (GeoJSON LineString)؛ کلید از window.NESHAN_MAP_KEY.
 */
(function () {
  var mapKey = typeof window !== 'undefined' && window.NESHAN_MAP_KEY;
  if (!mapKey || typeof nmp_mapboxgl === 'undefined') return;

  var TEHRAN_LNG = 51.3347;
  var TEHRAN_LAT = 35.7219;
  var DEFAULT_ZOOM = 12;
  var routeLayerId = 'team13-route-line';
  var routeSourceId = 'team13-route-source';
  var layerStore = {}; // id -> { remove: fn } for removeLayer/hasLayer

  var rawMap = new nmp_mapboxgl.Map({
    mapType: nmp_mapboxgl.Map.mapTypes.neshanVector,
    container: 'map-container',
    zoom: DEFAULT_ZOOM,
    pitch: 0,
    center: [TEHRAN_LNG, TEHRAN_LAT],
    minZoom: 2,
    maxZoom: 21,
    trackResize: true,
    mapKey: mapKey,
    poi: true,
    traffic: true,
    mapTypeControllerOptions: {
      show: true,
      position: 'bottom-left'
    }
  });

  function wrapMap(map) {
    var eventHandlers = { click: [], mousedown: [], mouseup: [], mouseout: [], mouseleave: [], popupopen: [] };

    function makeClickPayload(e) {
      return { latlng: { lat: e.lngLat.lat, lng: e.lngLat.lng } };
    }
    function makePointerPayload(e) {
      var pt = e.point;
      return {
        containerPoint: pt ? { x: pt.x, y: pt.y } : null,
        latlng: e.lngLat ? { lat: e.lngLat.lat, lng: e.lngLat.lng } : null
      };
    }

    function onMapEvent(event, fn) {
      if (!eventHandlers[event]) eventHandlers[event] = [];
      var wrapperFn = function (e) {
        var payload = event === 'click' ? makeClickPayload(e) : makePointerPayload(e);
        if (!payload.latlng && e.lngLat) payload.latlng = { lat: e.lngLat.lat, lng: e.lngLat.lng };
        fn(payload);
      };
      eventHandlers[event].push({ userFn: fn, wrapperFn: wrapperFn });
      if ((event === 'mouseout' || event === 'mouseleave') && typeof map.getContainer === 'function') {
        var container = map.getContainer();
        if (container) container.addEventListener(event, wrapperFn);
      } else {
        map.on(event, wrapperFn);
      }
      return this;
    }

    function offMapEvent(event, fn) {
      var list = eventHandlers[event];
      if (!list) return this;
      for (var i = 0; i < list.length; i++) {
        if (list[i].userFn === fn) {
          var w = list[i].wrapperFn;
          if ((event === 'mouseout' || event === 'mouseleave') && typeof map.getContainer === 'function') {
            var container = map.getContainer();
            if (container) container.removeEventListener(event, w);
          } else {
            map.off(event, w);
          }
          list.splice(i, 1);
          break;
        }
      }
      return this;
    }

    return {
      _map: map,
      setView: function (center, zoom) {
        var lng = center[1], lat = center[0];
        if (center.lng != null) { lng = center.lng; lat = center.lat; }
        map.flyTo({ center: [lng, lat], zoom: zoom || DEFAULT_ZOOM });
        return this;
      },
      getCenter: function () {
        var c = map.getCenter();
        return { lat: c.lat, lng: c.lng };
      },
      getZoom: function () { return map.getZoom(); },
      flyTo: function (center, zoom, opts) {
        var lng = center[1], lat = center[0];
        if (center.lng != null) { lng = center.lng; lat = center.lat; }
        map.flyTo({ center: [lng, lat], zoom: zoom || map.getZoom(), duration: (opts && opts.duration) || 0.5 });
      },
      invalidateSize: function () { map.resize(); },
      createPane: function (name) {
        return { style: { zIndex: 1000 } };
      },
      getPane: function (name) {
        return null;
      },
      on: function (event, fn) {
        if (event === 'click' || event === 'mousedown' || event === 'mouseup' || event === 'mouseout' || event === 'mouseleave') {
          return onMapEvent(event, fn);
        }
        if (event === 'popupopen') {
          if (!eventHandlers.popupopen) eventHandlers.popupopen = [];
          eventHandlers.popupopen.push(fn);
        }
        return this;
      },
      off: function (event, fn) {
        if (event === 'click' || event === 'mousedown' || event === 'mouseup' || event === 'mouseout' || event === 'mouseleave') {
          return offMapEvent(event, fn);
        }
        if (event === 'popupopen' && eventHandlers.popupopen) {
          eventHandlers.popupopen = eventHandlers.popupopen.filter(function (f) { return f !== fn; });
        }
        return this;
      },
      _firePopupOpen: function (popupRef) {
        (eventHandlers.popupopen || []).forEach(function (fn) { fn({ popup: popupRef }); });
      },
      containerPointToLatLng: function (containerPoint) {
        if (!containerPoint || (containerPoint.x == null && containerPoint.y == null)) return null;
        var x = containerPoint.x != null ? containerPoint.x : 0;
        var y = containerPoint.y != null ? containerPoint.y : 0;
        try {
          var lngLat = map.unproject([x, y]);
          return { lat: lngLat.lat, lng: lngLat.lng };
        } catch (err) {
          return null;
        }
      },
      removeLayer: function (layer) {
        if (layer && typeof layer.remove === 'function') {
          layer.remove();
          return;
        }
        if (layer && layer._layerId && map.getLayer(layer._layerId)) {
          map.removeLayer(layer._layerId);
          if (layer._sourceId) map.removeSource(layer._sourceId);
        }
      },
      hasLayer: function (layer) {
        if (!layer) return false;
        if (layer._onMap === true) return true;
        if (layer._layerId) return !!map.getLayer(layer._layerId);
        return false;
      },
      fitBounds: function (bounds, opts) {
        if (!bounds || typeof bounds.getSouthWest !== 'function' || typeof bounds.getNorthEast !== 'function') return;
        var padding = (opts && opts.padding) || [40, 40];
        var sw = bounds.getSouthWest();
        var ne = bounds.getNorthEast();
        map.fitBounds([[sw.lng, sw.lat], [ne.lng, ne.lat]], { padding: padding });
      },
      getBounds: function () {
        var b = map.getBounds();
        return {
          getSouthWest: function () { return { lat: b.getSouth(), lng: b.getWest() }; },
          getNorthEast: function () { return { lat: b.getNorth(), lng: b.getEast() }; }
        };
      },
      getContainer: function () {
        return (typeof map.getContainer === 'function' && map.getContainer()) || null;
      }
    };
  }

  var mapWrapper = wrapMap(rawMap);

  // --- L.marker با پشتیبانی از divIcon، draggable و پاپ‌آپ (مطابق مارکر سفارشی نشان) ---
  // مستندات: https://platform.neshan.org/docs/sdk/web/mapboxgl/examples/neshan-mapbox-custom-marker/
  function createMarker(latlng, opts) {
    opts = opts || {};
    var lat = Array.isArray(latlng) ? latlng[0] : latlng.lat;
    var lng = Array.isArray(latlng) ? latlng[1] : latlng.lng;
    var icon = opts.icon || null;
    var draggable = opts.draggable === true;
    var markerColor = opts.color || '#40916c';
    var el;
    if (icon && icon.options && icon.options.html) {
      el = document.createElement('div');
      el.innerHTML = icon.options.html;
      el.className = (icon.options.className || '') + ' team13-neshan-marker';
      el.style.width = (icon.options.iconSize && icon.options.iconSize[0]) + 'px' || '32px';
      el.style.height = (icon.options.iconSize && icon.options.iconSize[1]) + 'px' || '32px';
      el.style.cursor = 'pointer';
    } else {
      el = document.createElement('div');
      el.className = 'team13-neshan-marker-default';
      el.style.width = '24px'; el.style.height = '24px';
      el.style.background = markerColor; el.style.borderRadius = '50%';
      el.style.border = '2px solid #1b4332';
      el.style.cursor = draggable ? 'move' : 'pointer';
    }
    var marker = new nmp_mapboxgl.Marker({ element: el, draggable: draggable }).setLngLat([lng, lat]);
    var popupInstance = null;
    el.addEventListener('click', function (ev) {
      if (ev && ev.stopPropagation) ev.stopPropagation();
      if (ev && ev.preventDefault) ev.preventDefault();
      if (popupInstance && typeof marker.togglePopup === 'function') marker.togglePopup();
    });
    var wrapper = {
      _marker: marker,
      _onMap: false,
      bindPopup: function (content) {
        popupInstance = new nmp_mapboxgl.Popup({ offset: 25 });
        if (content instanceof window.HTMLElement) {
          if (typeof popupInstance.setDOMContent === 'function') popupInstance.setDOMContent(content);
          else popupInstance.setHTML(content.innerHTML || '');
        } else {
          popupInstance.setHTML(typeof content === 'string' ? content : '');
        }
        if (typeof popupInstance.on === 'function') {
          popupInstance.on('open', function () {
            if (wrapper._popupopen) wrapper._popupopen();
            if (mapWrapper && typeof mapWrapper._firePopupOpen === 'function') mapWrapper._firePopupOpen(wrapper.getPopup());
          });
        }
        marker.setPopup(popupInstance);
        return this;
      },
      getPopup: function () {
        if (!popupInstance) return null;
        return {
          getElement: function () {
            return (typeof popupInstance.getElement === 'function' && popupInstance.getElement()) || null;
          },
          setContent: function (c) {
            if (c instanceof window.HTMLElement) {
              if (typeof popupInstance.setDOMContent === 'function') popupInstance.setDOMContent(c);
              else popupInstance.setHTML(c.innerHTML);
            } else {
              popupInstance.setHTML(typeof c === 'string' ? c : '');
            }
          }
        };
      },
      togglePopup: function () {
        if (marker && typeof marker.togglePopup === 'function') marker.togglePopup();
        return this;
      },
      openPopup: function () {
        if (marker && typeof marker.togglePopup === 'function') marker.togglePopup();
        return this;
      },
      on: function (ev, fn) {
        if (ev === 'popupopen') this._popupopen = fn;
        if (ev === 'dragend') {
          this._dragend = fn;
          if (typeof marker.on === 'function') {
            marker.on('dragend', function () {
              var lngLat = marker.getLngLat();
              if (lngLat) { lat = lngLat.lat; lng = lngLat.lng; }
              if (wrapper._dragend) wrapper._dragend();
            });
          }
        }
        return this;
      },
      addTo: function (mapRef) {
        if (!this._onMap && this._marker && typeof this._marker.addTo === 'function') {
          this._marker.addTo(rawMap);
          this._onMap = true;
        }
        return this;
      },
      getLatLng: function () { return { lat: lat, lng: lng }; },
      setLatLng: function (ll) {
        var la = Array.isArray(ll) ? ll[0] : ll.lat;
        var ln = Array.isArray(ll) ? ll[1] : ll.lng;
        lat = la; lng = ln;
        marker.setLngLat([ln, la]);
        return this;
      },
      remove: function () {
        if (this._marker && typeof this._marker.remove === 'function') this._marker.remove();
        this._onMap = false;
      }
    };
    return wrapper;
  }

  // --- L.polyline برای رسم مسیر ---
  function createPolyline(latlngs, opts) {
    opts = opts || {};
    var id = routeSourceId + '-' + Date.now();
    var coords = latlngs.map(function (p) {
      var lat = Array.isArray(p) ? p[0] : p.lat;
      var lng = Array.isArray(p) ? p[1] : p.lng;
      return [lng, lat];
    });
    rawMap.addSource(id, {
      type: 'geojson',
      data: { type: 'Feature', properties: {}, geometry: { type: 'LineString', coordinates: coords } }
    });
    rawMap.addLayer({
      id: id + '-layer',
      type: 'line',
      source: id,
      layout: { 'line-join': 'round', 'line-cap': 'round' },
      paint: {
        'line-color': opts.color || '#40916c',
        'line-width': opts.weight || 6,
        'line-opacity': opts.opacity != null ? opts.opacity : 1
      }
    });
    var layerRef = {
      _layerId: id + '-layer',
      _sourceId: id,
      remove: function () {
        if (rawMap.getLayer(this._layerId)) rawMap.removeLayer(this._layerId);
        if (rawMap.getSource(this._sourceId)) rawMap.removeSource(this._sourceId);
      },
      addTo: function () { return this; },
      getBounds: function () {
        var minLng = coords[0][0], maxLng = coords[0][0], minLat = coords[0][1], maxLat = coords[0][1];
        coords.forEach(function (c) {
          if (c[0] < minLng) minLng = c[0];
          if (c[0] > maxLng) maxLng = c[0];
          if (c[1] < minLat) minLat = c[1];
          if (c[1] > maxLat) maxLat = c[1];
        });
        return {
          getSouthWest: function () { return { lat: minLat, lng: minLng }; },
          getNorthEast: function () { return { lat: maxLat, lng: maxLng }; }
        };
      },
      bringToFront: function () {}
    };
    return layerRef;
  }

  // --- L.circle (دایرهٔ شعاع بر حسب متر؛ تقریب با چندضلعی در Mapbox) ---
  function createCircle(center, opts) {
    opts = opts || {};
    var lat = Array.isArray(center) ? center[0] : center.lat;
    var lng = Array.isArray(center) ? center[1] : center.lng;
    var radiusM = opts.radius || 1000;
    var points = 64;
    var coords = [];
    for (var i = 0; i <= points; i++) {
      var angle = (i / points) * 2 * Math.PI;
      var dy = (radiusM / 111320) * Math.cos(angle);
      var dx = (radiusM / (111320 * Math.cos(lat * Math.PI / 180))) * Math.sin(angle);
      coords.push([lng + dx, lat + dy]);
    }
    var id = 'team13-circle-' + Date.now();
    rawMap.addSource(id, {
      type: 'geojson',
      data: { type: 'Feature', properties: {}, geometry: { type: 'Polygon', coordinates: [coords] } }
    });
    rawMap.addLayer({
      id: id + '-fill',
      type: 'fill',
      source: id,
      paint: {
        'fill-color': opts.fillColor || '#40916c',
        'fill-opacity': opts.fillOpacity != null ? opts.fillOpacity : 0.12
      }
    });
    rawMap.addLayer({
      id: id + '-line',
      type: 'line',
      source: id,
      paint: {
        'line-color': opts.color || '#40916c',
        'line-width': opts.weight || 2
      }
    });
    return {
      _circleIds: [id + '-fill', id + '-line', id],
      _onMap: true,
      addTo: function () { return this; },
      remove: function () {
        var ids = this._circleIds;
        if (ids[0] && rawMap.getLayer(ids[0])) rawMap.removeLayer(ids[0]);
        if (ids[1] && rawMap.getLayer(ids[1])) rawMap.removeLayer(ids[1]);
        if (ids[2] && rawMap.getSource(ids[2])) rawMap.removeSource(ids[2]);
        this._onMap = false;
      }
    };
  }

  // --- L.layerGroup (برای گروه مارکرها در map_data؛ مارکرها با createMarker خودشان addTo(rawMap) می‌شوند) ---
  function createLayerGroup() {
    var layers = [];
    return {
      _layers: layers,
      addTo: function (map) { return this; },
      addLayer: function (layer) {
        layers.push(layer);
        return this;
      },
      remove: function () {
        layers.forEach(function (l) {
          if (l && typeof l.remove === 'function') l.remove();
        });
        layers.length = 0;
      },
      clearLayers: function () {
        this.remove();
      },
      getBounds: function () {
        var minLat = Infinity, maxLat = -Infinity, minLng = Infinity, maxLng = -Infinity;
        layers.forEach(function (l) {
          var ll = l && l.getLatLng && l.getLatLng();
          if (ll && ll.lat != null && ll.lng != null) {
            if (ll.lat < minLat) minLat = ll.lat;
            if (ll.lat > maxLat) maxLat = ll.lat;
            if (ll.lng < minLng) minLng = ll.lng;
            if (ll.lng > maxLng) maxLng = ll.lng;
          }
        });
        if (minLat === Infinity) return null;
        return {
          getSouthWest: function () { return { lat: minLat, lng: minLng }; },
          getNorthEast: function () { return { lat: maxLat, lng: maxLng }; }
        };
      },
      eachLayer: function (fn) {
        layers.forEach(fn);
      }
    };
  }

  // --- L.popup (پشتیبانی از setContent(DOM) و getElement برای popupopen) ---
  function createPopup(opts) {
    opts = opts || {};
    var popup = new nmp_mapboxgl.Popup({ className: opts.className || '', offset: 25 });
    var self = {
      setLatLng: function (latlng) {
        var lat = Array.isArray(latlng) ? latlng[0] : latlng.lat;
        var lng = Array.isArray(latlng) ? latlng[1] : latlng.lng;
        this._lngLat = [lng, lat];
        return this;
      },
      setContent: function (htmlOrEl) {
        this._content = htmlOrEl;
        return this;
      },
      getElement: function () {
        return (typeof popup.getElement === 'function' && popup.getElement()) || null;
      },
      openOn: function (mapRef) {
        if (!this._lngLat) return this;
        popup.setLngLat(this._lngLat);
        if (this._content instanceof window.HTMLElement) {
          if (typeof popup.setDOMContent === 'function') popup.setDOMContent(this._content);
          else popup.setHTML(this._content.innerHTML);
        } else if (this._content) {
          popup.setHTML(typeof this._content === 'string' ? this._content : String(this._content));
        }
        popup.addTo(rawMap);
        var wrapper = window.team13MapInstance;
        if (wrapper && typeof wrapper._firePopupOpen === 'function') wrapper._firePopupOpen(self);
        return this;
      }
    };
    return self;
  }

  // --- L.divIcon برای مارکرهای سفارشی ---
  function createDivIcon(options) {
    return { options: options || {} };
  }

  // --- L.tileLayer بدون‌عمل (نقشهٔ نشان تایل خودش را دارد) ---
  function tileLayer() {
    return { addTo: function () { return this; } };
  }

  // --- L.DomEvent ---
  var DomEvent = {
    on: function (el, type, fn) {
      if (el && el.addEventListener) el.addEventListener(type, fn);
    },
    stopPropagation: function (e) {
      if (e && e.stopPropagation) e.stopPropagation();
    }
  };

  // --- L.map: برگرداندن wrapper نقشه ---
  function map(containerId) {
    return mapWrapper;
  }

  window.L = {
    map: map,
    marker: createMarker,
    polyline: createPolyline,
    circle: createCircle,
    popup: function (opts) { return createPopup(opts || {}); },
    divIcon: createDivIcon,
    tileLayer: tileLayer,
    layerGroup: createLayerGroup,
    DomEvent: DomEvent,
    Icon: { Default: {} },
    point: function (x, y) { return { x: x, y: y }; }
  };

  window.team13MapInstance = mapWrapper;
  window.team13NeshanMap = rawMap;

  rawMap.on('load', function () {
    if (typeof window.team13MapDataReady === 'function') window.team13MapDataReady();
  });
})();
