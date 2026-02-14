(function () {
  "use strict";

  var PERSIAN_DIGITS = "۰۱۲۳۴۵۶۷۸۹";

  function toPersianDigits(text) {
    return String(text).replace(/\d/g, function (digit) {
      return PERSIAN_DIGITS[digit];
    });
  }

  function hasNoConvert(el) {
    if (!el || !el.closest) return false;
    return el.closest(".no-digit-convert, .t10-no-digit") !== null;
  }

  function isForbiddenParent(el) {
    if (!el || !el.closest) return false;
    return (
      el.closest("script, style, input, textarea, select, option") !== null ||
      el.closest('[contenteditable="true"]') !== null
    );
  }

  function shouldSkipNode(node) {
    if (!node || !node.parentElement) return true;
    if (hasNoConvert(node.parentElement)) return true;
    if (isForbiddenParent(node.parentElement)) return true;
    return false;
  }

  function convertTextNode(node) {
    if (!node || !node.nodeValue) return;
    if (shouldSkipNode(node)) return;
    if (!/\d/.test(node.nodeValue)) return;
    node.nodeValue = toPersianDigits(node.nodeValue);
  }

  function convertWithin(root) {
    if (!root) return;

    if (root.nodeType === Node.TEXT_NODE) {
      convertTextNode(root);
      return;
    }

    if (root.nodeType === Node.ELEMENT_NODE && hasNoConvert(root)) {
      return;
    }

    var walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT, null);
    var current;
    while ((current = walker.nextNode())) {
      convertTextNode(current);
    }
  }

  function initObserver() {
    if (!("MutationObserver" in window)) return;
    var observer = null;
    var isProcessing = false;

    function handleMutations(mutations) {
      if (isProcessing) return;
      isProcessing = true;
      if (observer) observer.disconnect();

      mutations.forEach(function (mutation) {
        if (mutation.type === "characterData") {
          convertTextNode(mutation.target);
          return;
        }

        mutation.addedNodes.forEach(function (node) {
          if (node.nodeType === Node.TEXT_NODE) {
            convertTextNode(node);
          } else if (node.nodeType === Node.ELEMENT_NODE) {
            convertWithin(node);
          }
        });
      });

      if (observer) {
        observer.observe(document.body, {
          childList: true,
          subtree: true,
          characterData: true
        });
      }
      isProcessing = false;
    }

    observer = new MutationObserver(handleMutations);
    observer.observe(document.body, {
      childList: true,
      subtree: true,
      characterData: true
    });
  }

  function init() {
    convertWithin(document.body);
    initObserver();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
