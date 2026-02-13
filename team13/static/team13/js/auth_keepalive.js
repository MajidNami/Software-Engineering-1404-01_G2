/**
 * تمدید نشست احراز هویت (JWT) هر چند دقیقه تا کاربر لاگین بماند.
 * با فراخوانی /api/auth/refresh/ کوکی access_token و refresh_token به‌روز می‌شوند.
 */
(function () {
  var REFRESH_INTERVAL_MS = 10 * 60 * 1000; // 10 دقیقه

  function refreshAuth() {
    fetch("/api/auth/refresh/", {
      method: "POST",
      credentials: "same-origin",
      headers: { "Content-Type": "application/json", "Accept": "application/json" },
      body: "{}",
    }).catch(function () {});
  }

  if (typeof setInterval !== "undefined") {
    setInterval(refreshAuth, REFRESH_INTERVAL_MS);
    // یک بار بلافاصله پس از چند ثانیه (اگر کاربر لاگین است توکن تازه شود)
    setTimeout(refreshAuth, 5000);
  }
})();
