// Function to inject templates and set active page
function injectTemplates() {
  // Inject header
  fetch("/templates/header.html")
    .then((response) => response.text())
    .then((data) => {
      document.getElementById("header-placeholder").outerHTML = data;
      setActivePage();
    });

  // Inject footer
  fetch("/templates/footer.html")
    .then((response) => response.text())
    .then((data) => {
      document.getElementById("footer-placeholder").outerHTML = data;
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

// Run when DOM is loaded
document.addEventListener("DOMContentLoaded", injectTemplates);
