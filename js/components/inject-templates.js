// inject-templates.js injects nothing, and the name is kept deliberately.
//
// Until Wave 2 Phase 7 this file fetched templates/header.html and
// templates/footer.html at page load and swapped them into two placeholder
// divs. They are baked into the page at build time now, so all that is left
// here is the navigation: the mobile #navPanel and #titleBar, built from #nav
// by util.js's navList plugin, and the dropotron dropdown init.
//
// Renaming it to nav.js was built and measured, and reverted. It costs a
// one-line edit to all 463 pages, changes a published asset URL, and breaks
// three of the harness's ten assertions on a commit whose only content is a
// rename. css/fontawesome-all.min.css settled the identical trade already -
// DO-NOT-BREAK.md records that it "is a subset and its name is a lie...
// renaming it would mean editing 463 <head> blocks to gain nothing, so it
// keeps the name and says so in a comment at the top".
//
// Wave 4.10 rewrites this file to drop jQuery and dropotron and rewrites the
// script tail on all 463 pages anyway. The rename is free at that point and
// costs a second sitewide rewrite before it.

// Global variable for body element
var $body = $(document.body);

// Function to fully initialize the navigation system
function initNavigation() {
  // Remove existing elements to avoid duplicates on re-init
  $("#navPanel").remove();
  $("#titleBar").remove();
  // Remove any previously bound namespaced events from earlier inits
  $body.off("click.navPanel touchend.navPanel");
  $(document).off("keydown.navPanel");

  // Use a <button> (not <a href="#navPanel">) so the panel plugin's
  // anchor-based toggle handler never fires — that conflict was the bug.
  var $titleBar = $(
    '<div id="titleBar">' +
      '<button id="nav-toggle-btn" class="toggle"' +
        ' aria-label="Open navigation menu"' +
        ' aria-expanded="false"' +
        ' aria-controls="navPanel">' +
      "</button>" +
    "</div>"
  ).appendTo($body);

  // Build navPanel as a <nav> so it carries semantic meaning standalone
  var $navPanel = $(
    '<nav id="navPanel"' +
      ' role="navigation"' +
      ' aria-label="Mobile navigation"' +
      ' aria-hidden="true">' +
    $("#nav").navList() +
    "</nav>"
  ).appendTo($body);

  var $toggleBtn = $titleBar.find("#nav-toggle-btn");

  function openNav() {
    $body.addClass("navPanel-visible");
    $navPanel.attr("aria-hidden", "false");
    $toggleBtn
      .attr("aria-expanded", "true")
      .attr("aria-label", "Close navigation menu");
  }

  function closeNav() {
    $body.removeClass("navPanel-visible");
    $navPanel.attr("aria-hidden", "true");
    $toggleBtn
      .attr("aria-expanded", "false")
      .attr("aria-label", "Open navigation menu");
  }

  // Toggle button — stopPropagation prevents the body handler below from
  // immediately closing the panel on the same event that just opened it
  $toggleBtn.on("click", function (e) {
    e.stopPropagation();
    if ($body.hasClass("navPanel-visible")) {
      closeNav();
    } else {
      openNav();
    }
  });

  // Click or tap anywhere outside the panel / titleBar closes it.
  // Namespaced so re-init can cleanly remove the previous handler.
  $body.on("click.navPanel touchend.navPanel", function (e) {
    if (
      $body.hasClass("navPanel-visible") &&
      !$(e.target).closest("#navPanel, #titleBar").length
    ) {
      closeNav();
    }
  });

  // Prevent touches/clicks inside the panel from bubbling to the body handler
  $navPanel.on("click touchend", function (e) {
    e.stopPropagation();
  });

  // Escape key closes the panel and returns focus to the toggle button
  $(document).on("keydown.navPanel", function (e) {
    if (e.key === "Escape" && $body.hasClass("navPanel-visible")) {
      closeNav();
      $toggleBtn.trigger("focus");
    }
  });

  // Swipe left on the panel to close (threshold: 50px)
  var swipeStartX = null;
  $navPanel
    .on("touchstart", function (e) {
      swipeStartX = e.originalEvent.touches[0].pageX;
    })
    .on("touchmove", function (e) {
      if (swipeStartX === null) return;
      if (e.originalEvent.touches[0].pageX - swipeStartX < -50) {
        swipeStartX = null;
        closeNav();
      }
    })
    .on("touchend", function () {
      swipeStartX = null;
    });

  // Reinitialize Dropotron dropdown menus for desktop
  if (typeof $.fn.dropotron !== "undefined") {
    $("#nav > ul").dropotron({
      mode: "fade",
      noOpenerFade: true,
      alignment: "center",
    });
  }
}

// Run when DOM is loaded and jQuery is ready. The header and footer are in
// the page already - Wave 2 Phase 7 bakes them in at build time - so there is
// nothing to fetch and nothing to wait for, and this runs at DOMContentLoaded
// instead of 50ms after two network round trips came back.
$(function () {
  initNavigation();
});
