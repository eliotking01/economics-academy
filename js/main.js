/*
	Dopetrope by HTML5 UP
	html5up.net | @ajlkn
	Free for personal and commercial use under the CCA 3.0 license (html5up.net/license)

	Wave 4.10: the jQuery wrapper is gone. Neither statement below ever needed
	it - breakpoints.js is standalone and takes a plain object, and removing a
	class is one call. Nothing else in this file changed.

	Wave 4.11: the breakpoints() call is gone too, and the library with it. It
	named four widths - xlarge, large, medium and small - and then nothing ever
	asked which was active: no breakpoints.on() handler existed anywhere on the
	site, and the library writes no class and touches no DOM. The site's real
	breakpoints are the @media queries in css/main.css, which never went
	through it. What is left here is the is-preload line and nothing else.
*/

(function () {
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
