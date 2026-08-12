/*
	Dopetrope by HTML5 UP
	html5up.net | @ajlkn
	Free for personal and commercial use under the CCA 3.0 license (html5up.net/license)

	Wave 4.10: the jQuery wrapper is gone. Neither statement below ever needed
	it - breakpoints.js is standalone and takes a plain object, and removing a
	class is one call. Nothing else in this file changed.
*/

(function () {
  // Breakpoints.
  breakpoints({
    xlarge: ["1281px", "1680px"],
    large: ["981px", "1280px"],
    medium: ["737px", "980px"],
    small: [null, "736px"],
  });

  // Play initial animations on page load.
  //
  // body.is-preload suppresses every transition and animation on the page
  // (css/main.css:230). Dropping it 100 ms after load is what stops the
  // page animating its way in while it is still settling.
  window.addEventListener("load", function () {
    window.setTimeout(function () {
      document.body.classList.remove("is-preload");
    }, 100);
  });
})();
