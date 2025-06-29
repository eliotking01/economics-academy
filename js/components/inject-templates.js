// Global variable for body element
var $body = $(document.body);

// Function to fully initialize the navigation system
function initNavigation() {
  // Remove existing elements to avoid duplicates
  $("#navPanel").remove();
  $("#titleBar").remove();

  // Create title bar toggle button
  var $titleBar = $(
    '<div id="titleBar"><a href="#navPanel" class="toggle"></a></div>'
  ).appendTo($body);

  // Create navPanel with current navigation content
  var $navPanel = $(
    '<div id="navPanel"><nav>' + $("#nav").navList() + "</nav></div>"
  ).appendTo($body);

  // Initialize panel with all original settings
  $navPanel.panel({
    delay: 500,
    hideOnClick: true,
    hideOnSwipe: true,
    resetScroll: true,
    resetForms: true,
    side: "left",
    target: $body,
    visibleClass: "navPanel-visible",
  });

  // Rebind click event to the toggle button
  $titleBar
    .find(".toggle")
    .off("click")
    .on("click", function (e) {
      e.preventDefault();
      $navPanel.toggleClass("visible");
      $body.toggleClass("navPanel-visible");
    });

  // Reinitialize Dropotron menus
  if (typeof $.fn.dropotron !== "undefined") {
    $("#nav > ul").dropotron({
      mode: "fade",
      noOpenerFade: true,
      alignment: "center",
    });
  }
}

// Function to inject templates and set active page
function injectTemplates() {
  // Inject header
  fetch("/templates/header.html")
    .then((response) => response.text())
    .then((data) => {
      document.getElementById("header-placeholder").outerHTML = data;
      setActivePage();

      // Initialize navigation after slight delay to ensure DOM is ready
      setTimeout(initNavigation, 50);
    })
    .catch((error) => {
      console.error("Error loading header:", error);
    });

  // Inject footer
  fetch("/templates/footer.html")
    .then((response) => response.text())
    .then((data) => {
      document.getElementById("footer-placeholder").outerHTML = data;
    })
    .catch((error) => {
      console.error("Error loading footer:", error);
    });
}

// Improved setActivePage function with better path matching
function setActivePage() {
  const path = window.location.pathname;

  // Create a mapping of URL patterns to page identifiers
  const pageMap = [
    {
      pattern: /^\/revision-notes\/aqa-a2-macro(\/|$)/,
      page: "revision-notes-aqa-a2-macro",
    },
    {
      pattern: /^\/revision-notes\/edexcel-as-micro(\/|$)/,
      page: "revision-notes-edexcel-as-micro",
    },
    // Add more specific patterns first
    { pattern: /^\/revision-notes(\/|$)/, page: "revision-notes" },
    { pattern: /^\/past-papers(\/|$)/, page: "past-papers" },
    { pattern: /^\/tutoring\.html$/, page: "tutoring" },
    { pattern: /^\/marking\.html$/, page: "marking" },
    { pattern: /^\/about\.html$/, page: "about" },
    { pattern: /^\/contact\.html$/, page: "contact" },
    { pattern: /^\/(index\.html)?$/, page: "home" }, // Matches both / and /index.html
  ];

  // Find current page by checking patterns in order
  let currentPage = "";
  for (const { pattern, page } of pageMap) {
    if (pattern.test(path)) {
      currentPage = page;
      break;
    }
  }

  // Set active class
  if (currentPage) {
    const activeElement = document.querySelector(
      `[data-page="${currentPage}"]`
    );
    if (activeElement) {
      activeElement.classList.add("current");
    }
  }
}

// Run when DOM is loaded and jQuery is ready
$(function () {
  injectTemplates();
});
